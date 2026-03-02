#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币种涨跌预判监控器
每天0点-2点分析10分钟上涨占比，预判全天走势
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Telegram配置（写死）
TG_BOT_TOKEN = "8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0"
TG_CHAT_ID = "-1003227444260"

def send_telegram_message(message):
    """发送Telegram消息"""
    bot_token = TG_BOT_TOKEN
    chat_id = TG_CHAT_ID
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram消息发送成功")
            return True
        else:
            print(f"❌ Telegram消息发送失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 发送Telegram消息异常: {e}")
        return False

def fetch_coin_change_history(date=None):
    """获取指定日期0-2点的币种涨跌历史数据
    
    Args:
        date: 日期字符串，格式为YYYY-MM-DD，默认为今天（北京时间）
    """
    try:
        if date is None:
            # 使用北京时间获取当前日期
            now_utc = datetime.now(timezone.utc)
            now_beijing = now_utc + timedelta(hours=8)
            date = now_beijing.strftime('%Y-%m-%d')
        
        url = f"http://localhost:9002/api/coin-change-tracker/history?date={date}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            history = result.get('data', result)
            
            # 筛选0-2点的数据，并计算每条记录的上涨占比
            morning_records = []
            
            for record in history:
                time_str = record.get('beijing_time', '')
                if not time_str:
                    continue
                
                try:
                    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    hour = dt.hour
                    
                    # 只分析0-2点的数据
                    if 0 <= hour < 2:
                        changes = record.get('changes', {})
                        if changes:
                            # 计算这条记录的上涨占比
                            total_coins = len(changes)
                            up_coins = sum(1 for coin_data in changes.values() 
                                         if coin_data.get('change_pct', 0) > 0)
                            up_ratio = (up_coins / total_coins * 100) if total_coins > 0 else 0
                            
                            morning_records.append({
                                'time': time_str,
                                'up_ratio': up_ratio
                            })
                except Exception as e:
                    continue
            
            return {'records': morning_records, 'date': date}
        else:
            print(f"❌ 获取历史数据失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取历史数据异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_bar_colors(data):
    """
    分析10分钟柱状图颜色
    按10分钟分组，计算每组的平均上涨占比，然后判断颜色
    返回: {'green': count, 'red': count, 'yellow': count, 'blank': count, 'blank_ratio': float}
    
    规则:
    - 绿色: 平均上涨占比 > 55%
    - 红色: 平均上涨占比 < 45%且> 0  
    - 黄色: 45% <= 平均上涨占比 <= 55%
    - 空白: 平均上涨占比 == 0%
    """
    if not data or 'records' not in data:
        return None
    
    records = data['records']
    if not records:
        return None
    
    # 按10分钟分组，存储所有数据点
    interval = 10  # 10分钟
    grouped = defaultdict(lambda: {'ratios': []})  # 存储所有up_ratio而不是求和
    
    for record in records:
        time_str = record.get('time', '')
        up_ratio = record.get('up_ratio', 0)
        
        if not time_str:
            continue
        
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            hour = dt.hour
            minute = dt.minute
            
            # 计算属于哪个10分钟区间
            total_minutes = hour * 60 + minute
            group_index = total_minutes // interval
            
            grouped[group_index]['ratios'].append(up_ratio)
        except Exception as e:
            continue
    
    # 判断每个10分钟区间的颜色
    # 规则：只看区间平均上涨占比
    color_counts = {'green': 0, 'red': 0, 'yellow': 0, 'blank': 0}
    total_bars = len(grouped)
    
    for group_idx in sorted(grouped.keys()):
        ratios = grouped[group_idx]['ratios']
        if not ratios:
            continue
        
        # 计算平均值
        avg_up_ratio = sum(ratios) / len(ratios)
        
        # 根据平均值判断颜色
        if avg_up_ratio == 0:
            color_counts['blank'] += 1  # 空白（0%）
        elif avg_up_ratio > 55:
            color_counts['green'] += 1  # 绿色（>55%）
        elif avg_up_ratio >= 45:
            color_counts['yellow'] += 1  # 黄色（45%-55%）
        else:
            color_counts['red'] += 1  # 红色（<45%）
    
    # 计算空白占比
    color_counts['blank_ratio'] = (color_counts['blank'] / total_bars * 100) if total_bars > 0 else 0
    
    return color_counts

def fetch_after_2am_bars(date=None):
    """获取2点之后的前三根柱子数据（2:10、2:20、2:30三个10分钟区间）
    
    Args:
        date: 日期字符串，格式为YYYY-MM-DD，默认为今天（北京时间）
    
    Returns:
        dict: {
            'bars': [bar1_color, bar2_color, bar3_color],  # 三根柱子的颜色
            'bar_details': [详细信息列表],
            'success': True/False
        }
    """
    try:
        if date is None:
            now_utc = datetime.now(timezone.utc)
            now_beijing = now_utc + timedelta(hours=8)
            date = now_beijing.strftime('%Y-%m-%d')
        
        url = f"http://localhost:9002/api/coin-change-tracker/history?date={date}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            history = result.get('data', result)
            
            # 筛选特定时间区间的数据：2:10-2:20, 2:20-2:30, 2:30-2:40
            # 这三个10分钟区间对应图表上的三根柱子
            target_intervals = [
                (2, 10, 20),  # 2:10-2:20
                (2, 20, 30),  # 2:20-2:30
                (2, 30, 40),  # 2:30-2:40
            ]
            
            after_2am_records = []
            
            for hour, minute_start, minute_end in target_intervals:
                interval_data = []
                
                for record in history:
                    time_str = record.get('beijing_time', '')
                    if not time_str:
                        continue
                    
                    try:
                        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                        rec_hour = dt.hour
                        rec_minute = dt.minute
                        
                        # 检查是否在当前10分钟区间内
                        if rec_hour == hour and minute_start <= rec_minute < minute_end:
                            changes = record.get('changes', {})
                            if changes:
                                # 计算上涨占比
                                total_coins = len(changes)
                                up_coins = sum(1 for coin_data in changes.values() 
                                             if coin_data.get('change_pct', 0) > 0)
                                up_ratio = (up_coins / total_coins * 100) if total_coins > 0 else 0
                                
                                interval_data.append({
                                    'time': time_str,
                                    'up_ratio': up_ratio
                                })
                    except Exception as e:
                        continue
                
                # 计算这个10分钟区间的平均上涨占比
                if interval_data:
                    avg_up_ratio = sum(d['up_ratio'] for d in interval_data) / len(interval_data)
                    
                    # 判断颜色
                    if avg_up_ratio >= 60:
                        color = 'green'
                    elif avg_up_ratio <= 40:
                        color = 'red'
                    else:
                        color = 'yellow'
                    
                    # 使用区间的第一个时间点作为代表
                    after_2am_records.append({
                        'time': f'{date} {hour:02d}:{minute_start:02d}:00',
                        'up_ratio': avg_up_ratio,
                        'color': color
                    })
            
            # 应该正好有3根柱子
            bars = after_2am_records
            
            if len(bars) >= 3:
                return {
                    'bars': [bar['color'] for bar in bars],
                    'bar_details': bars,
                    'success': True
                }
            else:
                return {
                    'bars': [],
                    'bar_details': bars,
                    'success': False,
                    'message': f'数据不足，只有{len(bars)}根柱子'
                }
        else:
            return {'bars': [], 'bar_details': [], 'success': False, 'message': f'API返回错误: {response.status_code}'}
    except Exception as e:
        return {'bars': [], 'bar_details': [], 'success': False, 'message': f'异常: {str(e)}'}

def analyze_second_trigger(bars):
    """分析二级触发条件
    
    Args:
        bars: 三根柱子的颜色列表，例如 ['green', 'green', 'green']
    
    Returns:
        dict: {
            'triggered': True/False,  # 是否触发二级信号
            'action': 'immediate_long' / 'wait_dip_then_long' / None,  # 操作建议
            'description': 描述文字
        }
    """
    if len(bars) < 3:
        return {
            'triggered': False,
            'action': None,
            'description': '数据不足，无法判断二级触发'
        }
    
    # 统计三根柱子的颜色
    bar1, bar2, bar3 = bars[0], bars[1], bars[2]
    
    # 统计三根柱子中各颜色的数量
    green_count = sum(1 for b in bars if b == 'green')
    red_count = sum(1 for b in bars if b == 'red')
    blank_count = sum(1 for b in bars if b == 'blank')
    yellow_count = sum(1 for b in bars if b == 'yellow')
    
    # 情况1: 三根都是绿色 → 直接做多
    if green_count == 3:
        return {
            'triggered': True,
            'action': 'immediate_long',
            'description': '🟢🟢🟢 2点之后三根全绿，直接做多！',
            'detail': '二级触发【立即做多】：2点后连续三根绿色柱子，市场上涨趋势明确。'
        }
    
    # 情况2: 三根都是空白 → 大幅下跌后再做多
    if blank_count == 3:
        return {
            'triggered': True,
            'action': 'wait_dip_then_long',
            'description': '⚪⚪⚪ 2点之后三根全空白，等待大幅下跌后做多',
            'detail': '二级触发【等跌后做多】：2点后连续三根空白，市场将大幅下跌，等待跌透后再做多。'
        }
    
    # 情况3: 三根都是红色 → 大幅下跌后再做多（与全空白相同）
    if red_count == 3:
        return {
            'triggered': True,
            'action': 'wait_dip_then_long',
            'description': '🔴🔴🔴 2点之后三根全红，等待大幅下跌后做多',
            'detail': '二级触发【等跌后做多】：2点后连续三根红色柱子，市场持续下跌，等待跌透后再做多。'
        }
    
    # 情况4: 红色>=2根 + 空白 → 大幅下跌后再做多
    # 包括：红红空白、红空白红、空白红红
    if red_count >= 2 and blank_count >= 1 and green_count == 0:
        return {
            'triggered': True,
            'action': 'wait_dip_then_long',
            'description': f'🔴🔴⚪ 2点之后{red_count}根红色+{blank_count}根空白，等待大幅下跌后做多',
            'detail': f'二级触发【等跌后做多】：2点后{red_count}根红色+{blank_count}根空白，市场下跌趋势，等待跌透后再做多。'
        }
    
    # 情况5: 红色1根 + 空白>=2根 → 大幅下跌后再做多
    # 包括：红空白空白、空白红空白、空白空白红
    if red_count == 1 and blank_count >= 2 and green_count == 0:
        return {
            'triggered': True,
            'action': 'wait_dip_then_long',
            'description': f'🔴⚪⚪ 2点之后1根红色+{blank_count}根空白，等待大幅下跌后做多',
            'detail': f'二级触发【等跌后做多】：2点后1根红色+{blank_count}根空白，市场偏弱，等待跌透后再做多。'
        }
    
    # 其他情况：不触发二级信号
    bar_desc = '/'.join([bar1, bar2, bar3])
    return {
        'triggered': False,
        'action': None,
        'description': f'2点后柱子：{bar_desc}，不满足二级触发条件',
        'detail': None
    }

def determine_market_signal(color_counts):
    """
    根据颜色分布判断市场信号
    
    情况1: 有绿+有红+无黄 OR 有绿+有红+有黄但黄柱子只有1根 → 低吸
    情况1c（新增）: 有绿色柱子 + (有红色或有空白) + 绿色>=3根 → 低吸
    情况2: 有绿+有红+有黄 且黄柱子>=2根（大于1根） → 等待新低
    情况3: 只有红色 或 红色+空白（任何占比） → 做空
    情况4: 全部绿色 → 诱多不参与
    情况5: 全部为空白 → 空头强控盘，建议观望
    情况6: 红色+黄色（无绿色） → 观望
    情况7: 只有绿色+黄色（无红色），黄色>=2根 → 等待新低
    情况7b: 只有绿色+黄色（无红色），黄色只有1根 → 低吸
    
    注意：当信号为"低吸"时，需要在2点后检查二级触发条件
    """
    if not color_counts:
        return None, None
    
    green = color_counts['green']
    red = color_counts['red']
    yellow = color_counts['yellow']
    blank = color_counts.get('blank', 0)
    blank_ratio = color_counts.get('blank_ratio', 0)
    
    # 情况5: 全部为空白（空头强控盘）
    # 必须满足：全部是空白（100%空白），没有其他颜色
    if blank > 0 and green == 0 and red == 0 and yellow == 0:
        return "空头强控盘", "⚪⚪⚪ 0点-2点全部为空白，空头强控盘，建议观望。操作提示：不参与"
    
    # 情况4: 全部绿色（诱多）
    if green > 0 and red == 0 and yellow == 0 and blank == 0:
        return "诱多不参与", "🟢 全部绿色柱子，单边诱多行情，不参与操作。操作提示：不参与"
    
    # 情况3: 只有红色（或红色+空白）的判断（无绿色、无黄色） → 全部做空
    if red > 0 and green == 0 and yellow == 0:
        if blank == 0:
            return "做空", "🔴 只有红色柱子，预判下跌行情，建议做空。操作提示：相对高点做空"
        else:
            return "做空", f"🔴⚪ 红色+空白且空白占比{blank_ratio:.1f}%，预判下跌行情，建议做空。操作提示：相对高点做空"
    
    # 情况1: 有绿+有红+无黄 → 低吸（原始情况）
    if green > 0 and red > 0 and yellow == 0:
        return "低吸", "🟢🔴 有绿有红无黄，红色区间为低吸机会。操作提示：低点做多"
    
    # 情况2优先: 有绿+有红+有黄，且黄柱子 >= 2根（大于1根）→ 等待新低（新增逻辑）
    if green > 0 and red > 0 and yellow >= 2:
        return "等待新低", f"🟢🔴🟡 有绿有红有黄（黄色{yellow}根>=2根），可能还有新低，建议等待。操作提示：高点做空"
    
    # 情况1扩展: 有绿+有红+有黄，但(红+黄) < 3根 OR 黄柱子只有1根 → 低吸（保留原逻辑+新增）
    if green > 0 and red > 0 and yellow > 0:
        if (red + yellow) < 3 or yellow == 1:
            return "低吸", f"🟢🔴🟡 有绿有红有黄（红{red}+黄{yellow}共{red+yellow}根），红色区间为低吸机会。操作提示：低点做多"
    
    # 情况1c（新增）: 有绿色柱子 + (有红色或有空白) + 绿色>=3根 → 低吸
    # 适用场景：绿色柱子足够多(>=3根)，且有红色或空白柱子存在
    if green >= 3 and (red > 0 or blank > 0):
        if red > 0 and blank > 0:
            return "低吸", f"🟢🔴⚪ 绿色{green}根+红色{red}根+空白{blank}根，绿色柱子>=3根为主导，红色区间为低吸机会。操作提示：低点做多"
        elif red > 0:
            return "低吸", f"🟢🔴 绿色{green}根+红色{red}根，绿色柱子>=3根为主导，红色区间为低吸机会。操作提示：低点做多"
        else:  # blank > 0
            return "低吸", f"🟢⚪ 绿色{green}根+空白{blank}根，绿色柱子>=3根为主导，空白区间为低吸机会。操作提示：低点做多"
    
    # 情况7: 红色+黄色（无绿色）→ 观望
    # 必须满足：有红色、有黄色、没有绿色
    if red > 0 and yellow > 0 and green == 0:
        return "观望", "🔴🟡 红色柱子+黄色柱子，没有绿色柱子，多空博弈方向不明。操作提示：无，不参与"
    
    # 情况8: 只有绿色+黄色（无红色）→ 根据绿色数量判断
    if green > 0 and yellow > 0 and red == 0:
        # 如果绿色>=3根，判断为低吸（新增逻辑1c的扩展）
        if green >= 3:
            return "低吸", f"🟢🟡 绿色{green}根+黄色{yellow}根，绿色柱子>=3根为主导，黄色区间为低吸机会。操作提示：低点做多"
        # 否则观望
        return "观望", f"🟢🟡 只有绿色{green}根和黄色{yellow}根，绿色不足3根，无法判断低吸或新低。操作提示：观望"
    
    # 其他情况
    return "观望", "⚪ 柱状图混合分布，建议观望"

def save_prediction_data(color_counts, signal, description, is_temp=False, second_trigger=None):
    """保存预判数据到JSONL文件（按日期分文件）
    
    Args:
        color_counts: 颜色统计
        signal: 预判信号
        description: 描述
        is_temp: 是否为临时数据（0-2点之间）
        second_trigger: 二级触发信息（仅在低吸信号且2点后有效）
    """
    try:
        # 使用北京时间（UTC+8）
        now_utc = datetime.now(timezone.utc)
        now = now_utc + timedelta(hours=8)
        
        # 准备数据
        prediction_data = {
            "timestamp": now.strftime('%Y-%m-%d %H:%M:%S'),
            "date": now.strftime('%Y-%m-%d'),
            "analysis_time": now.strftime('%H:%M:%S'),
            "color_counts": color_counts,
            "signal": signal,
            "description": description,
            "is_temp": is_temp,  # 标记是否为临时数据
            "is_final": not is_temp  # 标记是否为最终预判（2点）
        }
        
        # 添加二级触发信息（如果有）
        if second_trigger:
            prediction_data["second_trigger"] = second_trigger
        
        # 统一使用JSONL格式，按日期分文件
        date_str = now.strftime('%Y%m%d')  # 格式：20260226
        prediction_dir = "/home/user/webapp/data/daily_predictions"
        os.makedirs(prediction_dir, exist_ok=True)
        
        # 文件名格式：prediction_YYYYMMDD.jsonl
        prediction_file = os.path.join(prediction_dir, f"prediction_{date_str}.jsonl")
        
        # 追加模式写入JSONL
        with open(prediction_file, 'a', encoding='utf-8') as f:
            json.dump(prediction_data, f, ensure_ascii=False)
            f.write('\n')
        
        if is_temp:
            print(f"📝 临时预判数据已追加到: {prediction_file}")
        else:
            print(f"💾 最终预判数据已保存到: {prediction_file}")
        
        # 兼容旧代码：同时保存最新数据到旧位置（JSON格式）
        old_file = "/home/user/webapp/data/daily_prediction.json"
        with open(old_file, 'w', encoding='utf-8') as f:
            json.dump(prediction_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ 保存预判数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_morning_analysis():
    """执行早晨0:10-2:00分析"""
    # 使用北京时间（UTC+8）
    now = datetime.now(timezone.utc)
    beijing_time = now + timedelta(hours=8)
    current_hour = beijing_time.hour
    current_minute = beijing_time.minute
    
    # 检查是否在分析时段
    in_analysis_period = False
    if current_hour == 0 and current_minute >= 10:
        in_analysis_period = True
    elif current_hour == 1:
        in_analysis_period = True
    elif current_hour == 2 and current_minute == 0:
        in_analysis_period = True
    
    if not in_analysis_period:
        print(f"⏰ 当前北京时间 {beijing_time.strftime('%H:%M')}，不在0:10-2:00分析时段")
        return
    
    print(f"\n{'='*60}")
    print(f"🔍 币种涨跌预判分析 - {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"{'='*60}")
    
    # 获取数据
    data = fetch_coin_change_history()
    if not data:
        print("❌ 无法获取数据，跳过本次分析")
        return
    
    # 分析柱状图颜色
    color_counts = analyze_bar_colors(data)
    if not color_counts:
        print("❌ 数据解析失败，跳过本次分析")
        return
    
    print(f"\n📊 柱状图颜色统计:")
    print(f"  🟢 绿色柱子: {color_counts['green']}根 (上涨占比 > 55%)")
    print(f"  🔴 红色柱子: {color_counts['red']}根 (上涨占比 < 45%)")
    print(f"  🟡 黄色柱子: {color_counts['yellow']}根 (45% ≤ 上涨占比 ≤ 55%)")
    print(f"  ⚪ 空白柱子: {color_counts.get('blank', 0)}根 (上涨占比 = 0%, 占比: {color_counts.get('blank_ratio', 0):.1f}%)")
    
    # 判断市场信号
    signal, description = determine_market_signal(color_counts)
    
    print(f"\n🎯 市场信号: {signal}")
    print(f"📝 说明: {description}")
    
    # 判断是否是2:00（生成最终预判）
    is_final = (current_hour == 2 and current_minute == 0)
    is_temp = not is_final
    
    # 二级触发检查（仅在2点且信号为"低吸"时）
    second_trigger_info = None
    if is_final and signal == "低吸":
        print(f"\n🔍 检测到【低吸】信号，开始二级触发分析...")
        print(f"📊 正在获取2点后前三根柱子数据（2:00-2:30）...")
        
        # 这里暂时不获取，因为2:00时还没有2:00-2:30的数据
        # 我们需要在2:30后单独运行一次二级触发检查
        print(f"⏰ 将在2:30后进行二级触发检查")
    
    # 保存预判数据
    save_prediction_data(color_counts, signal, description, is_temp=is_temp, second_trigger=second_trigger_info)
    
    # 只在2:00发送Telegram消息（最终预判）
    if is_final:
        # 构建Telegram消息
        blank_info = f"⚪ 空白: {color_counts.get('blank', 0)}根 (上涨占比 = 0%, 占比: {color_counts.get('blank_ratio', 0):.1f}%)\n" if color_counts.get('blank', 0) > 0 else ""
        
        message = f"""
<b>🔔 币种走势预判 - {beijing_time.strftime('%Y-%m-%d %H:%M')}</b>

<b>📊 柱状图颜色统计 (0-2点):</b>
🟢 绿色: {color_counts['green']}根 (上涨占比 &gt; 55%)
🔴 红色: {color_counts['red']}根 (上涨占比 &lt; 45%)
🟡 黄色: {color_counts['yellow']}根 (45% ≤ 占比 ≤ 55%)
{blank_info}
<b>🎯 预判信号: {signal}</b>
{description}

<b>📖 分析规则:</b>
• 情况1: 有绿+有红+无黄 OR 有绿+有红+有黄但黄柱子只有1根 → 低吸机会
• 情况1c: 有绿色(>=3根) + (有红色或有空白) → 低吸机会（新增）
• 情况2: 有绿+有红+有黄 且黄柱子>=2根（大于1根） → 等待新低
• 情况3: 纯红色 或 红色+空白（任何占比） → 做空信号
• 情况4: 全部绿色 → 诱多不参与
• 情况5: 全部为空白 → 空头强控盘，建议观望
• 情况6: 红色+黄色（无绿色） → 观望，不参与
• 情况7: 绿色+黄色（无红色），黄色>=2根 → 等待新低
• 情况7b: 绿色+黄色（无红色），黄色只有1根 → 低吸机会

⏰ 分析时段: 0:10 - 2:00
📈 数据来源: 10分钟上涨占比（共12根柱子）
"""
        
        # 如果是低吸信号，添加二级触发提示
        if signal == "低吸":
            message += "\n<b>🔔 二级触发检查：</b>将在2:30后检查2点后三根柱子，判断立即做多或等跌后做多"
        
        # 发送Telegram消息
        send_telegram_message(message.strip())
        print(f"📱 已发送Telegram通知")
    else:
        print(f"⏰ 当前 {beijing_time.strftime('%H:%M')}，临时数据保存，不发送Telegram")
    
    print(f"\n✅ 分析完成")

def check_missed_second_trigger():
    """启动时检查是否错过了今天的二级触发检查"""
    now_utc = datetime.now(timezone.utc)
    now_beijing = now_utc + timedelta(hours=8)
    current_date = now_beijing.date()
    current_hour = now_beijing.hour
    current_minute = now_beijing.minute
    
    # 如果当前时间在 2:30 - 23:59 之间，检查今天是否需要补做二级触发检查
    if current_hour >= 2 and current_minute >= 30:
        print(f"\n🔍 检查是否需要补做今天的二级触发检查...")
        print(f"⏰ 当前时间: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
        
        try:
            date_str = now_beijing.strftime('%Y%m%d')
            prediction_file = f"/home/user/webapp/data/daily_predictions/prediction_{date_str}.jsonl"
            
            if os.path.exists(prediction_file):
                with open(prediction_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_prediction = json.loads(lines[-1].strip())
                        signal = last_prediction.get('signal', '')
                        second_trigger = last_prediction.get('second_trigger')
                        
                        # 如果是"低吸"信号且还没有二级触发数据
                        if signal == "低吸" and second_trigger is None:
                            print(f"⚠️ 发现今天的【低吸】信号还未进行二级触发检查，立即补做...")
                            
                            # 获取2点后的三根柱子
                            after_2am_data = fetch_after_2am_bars()
                            
                            if after_2am_data['success']:
                                bars = after_2am_data['bars']
                                bar_details = after_2am_data['bar_details']
                                
                                print(f"\n📊 2点后前三根柱子:")
                                for i, detail in enumerate(bar_details, 1):
                                    color_emoji = {
                                        'green': '🟢',
                                        'red': '🔴',
                                        'yellow': '🟡',
                                        'blank': '⚪'
                                    }.get(detail['color'], '⚪')
                                    print(f"  柱子{i}: {color_emoji} {detail['color']} (上涨占比: {detail['up_ratio']:.1f}%, 时间: {detail['time']})")
                                
                                # 分析二级触发
                                trigger_result = analyze_second_trigger(bars)
                                
                                print(f"\n🎯 二级触发结果:")
                                print(f"  触发状态: {'✅ 已触发' if trigger_result['triggered'] else '⭕ 未触发'}")
                                print(f"  操作建议: {trigger_result.get('action', '无') or '无'}")
                                print(f"  描述: {trigger_result['description']}")
                                
                                # 更新预判数据，添加二级触发信息
                                last_prediction['second_trigger'] = {
                                    'checked_at': now_beijing.strftime('%Y-%m-%d %H:%M:%S'),
                                    'bars': bars,
                                    'bar_details': bar_details,
                                    'triggered': trigger_result['triggered'],
                                    'action': trigger_result.get('action'),
                                    'description': trigger_result['description'],
                                    'detail': trigger_result.get('detail')
                                }
                                
                                # 重新保存最后一行
                                lines[-1] = json.dumps(last_prediction, ensure_ascii=False) + '\n'
                                with open(prediction_file, 'w', encoding='utf-8') as f:
                                    f.writelines(lines)
                                
                                print(f"💾 二级触发信息已保存到: {prediction_file}")
                                
                                # 发送Telegram通知
                                if trigger_result['triggered']:
                                    action_text = {
                                        'immediate_long': '🚀 立即做多',
                                        'wait_dip_then_long': '⏳ 等待大跌后做多'
                                    }.get(trigger_result['action'], '未知')
                                    
                                    # 柱子颜色emoji
                                    color_emojis = []
                                    for detail in bar_details:
                                        emoji = {
                                            'green': '🟢',
                                            'red': '🔴',
                                            'yellow': '🟡',
                                            'blank': '⚪'
                                        }.get(detail['color'], '⚪')
                                        color_emojis.append(emoji)
                                    
                                    message = f"""
🔔 <b>【低吸】二级触发通知</b> 🔔

📅 日期: {now_beijing.strftime('%Y-%m-%d')}
⏰ 时间: {now_beijing.strftime('%H:%M')} (北京时间)

━━━━━━━━━━━━━━━━━━━━

📊 <b>今日预判: 低吸</b>

🔍 <b>2点后前三根柱子:</b>
{color_emojis[0]} 2:10 - 上涨占比 {bar_details[0]['up_ratio']:.1f}%
{color_emojis[1]} 2:20 - 上涨占比 {bar_details[1]['up_ratio']:.1f}%
{color_emojis[2]} 2:30 - 上涨占比 {bar_details[2]['up_ratio']:.1f}%

━━━━━━━━━━━━━━━━━━━━

✅ <b>二级触发: 已触发</b>
💡 <b>操作建议: {action_text}</b>

{trigger_result['description']}

━━━━━━━━━━━━━━━━━━━━

💬 <b>说明:</b>
{trigger_result.get('detail', '按二级触发策略执行')}

⚠️ <b>注意:</b> 此为补发通知（服务重启后检测到遗漏）

⚠️ <b>风险提示:</b> 请结合实际市场情况谨慎决策
"""
                                    send_telegram_message(message.strip())
                                    print(f"📱 已发送二级触发Telegram通知（补发）")
                                else:
                                    print(f"ℹ️ 未触发二级信号")
                                
                                print(f"✅ 补做二级触发检查完成")
                            else:
                                print(f"❌ 获取2点后数据失败: {after_2am_data.get('message', '未知错误')}")
                        else:
                            if signal == "低吸":
                                print(f"✅ 今天的【低吸】信号已完成二级触发检查")
                            else:
                                print(f"ℹ️ 今天的预判信号为【{signal}】，无需二级触发检查")
            else:
                print(f"ℹ️ 今天还没有预判数据")
        except Exception as e:
            print(f"❌ 检查二级触发时出错: {e}")

def main():
    """主函数 - 持续监控"""
    print("🚀 币种涨跌预判监控器启动")
    print("⏰ 监控时段: 每天 0:10 - 2:00 (北京时间)")
    print("📊 分析指标: 10分钟上涨占比")
    print("🔄 更新频率: 每10分钟（0:10, 0:20, 0:30, ..., 1:50, 2:00）")
    
    # 启动时检查是否错过了今天的二级触发检查
    check_missed_second_trigger()
    
    last_analysis_date = None
    
    while True:
        try:
            # 使用北京时间（UTC+8）
            now_utc = datetime.now(timezone.utc)
            now_beijing = now_utc + timedelta(hours=8)
            current_date = now_beijing.date()
            current_hour = now_beijing.hour
            current_minute = now_beijing.minute
            
            # 检查是否在分析时段：0:10 - 1:59 或 2:00整点
            in_analysis_period = False
            in_second_trigger_check = False  # 二级触发检查
            
            if current_hour == 0 and current_minute >= 10:
                in_analysis_period = True  # 0:10 - 0:59
            elif current_hour == 1:
                in_analysis_period = True  # 1:00 - 1:59
            elif current_hour == 2 and current_minute == 0:
                in_analysis_period = True  # 2:00 整点（最终预判）
            elif current_hour == 2 and current_minute == 30:
                in_second_trigger_check = True  # 2:30 整点（二级触发检查）
            
            if in_analysis_period:
                # 检查是否是新的一天，如果是则重置
                if last_analysis_date != current_date:
                    print(f"\n🆕 新的一天开始: {current_date}")
                    last_analysis_date = current_date
                
                print(f"\n⏰ 进入分析时段: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
                run_morning_analysis()
                
                # 等待到下一个10分钟整点（使用北京时间计算）
                next_minute = ((current_minute // 10) + 1) * 10
                if next_minute >= 60:
                    next_minute = 0
                    next_hour = current_hour + 1
                else:
                    next_hour = current_hour
                
                # 计算等待时间
                if current_hour == 2 and current_minute == 0:
                    # 刚完成2:00分析，等到2:30进行二级触发检查
                    next_run = now_beijing.replace(hour=2, minute=30, second=0, microsecond=0)
                    wait_seconds = (next_run - now_beijing).total_seconds()
                    print(f"⏳ 下次二级触发检查: {next_run.strftime('%H:%M')} (北京时间)")
                    print(f"💤 等待 {wait_seconds:.0f} 秒...")
                    time.sleep(max(1, wait_seconds))
                elif next_hour >= 2 and next_minute > 0:
                    # 已经过了2:00，等到明天
                    next_run = now_beijing.replace(hour=0, minute=10, second=0, microsecond=0) + timedelta(days=1)
                    wait_seconds = (next_run - now_beijing).total_seconds()
                    print(f"✅ 今日分析完成")
                    print(f"⏳ 下次分析时间: {next_run.strftime('%Y-%m-%d %H:%M')} (北京时间)")
                    print(f"💤 等待 {wait_seconds/3600:.1f} 小时...")
                    time.sleep(min(3600, wait_seconds))
                else:
                    # 等到下一个10分钟整点
                    next_run = now_beijing.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)
                    wait_seconds = (next_run - now_beijing).total_seconds()
                    print(f"⏳ 下次分析时间: {next_run.strftime('%H:%M')} (北京时间)")
                    print(f"💤 等待 {wait_seconds:.0f} 秒...")
                    time.sleep(wait_seconds)
            
            elif in_second_trigger_check:
                # 2:30 二级触发检查
                print(f"\n{'='*60}")
                print(f"🔔 二级触发检查 - {now_beijing.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
                print(f"{'='*60}")
                
                # 读取今天的预判数据，检查是否是"低吸"信号
                try:
                    date_str = now_beijing.strftime('%Y%m%d')
                    prediction_file = f"/home/user/webapp/data/daily_predictions/prediction_{date_str}.jsonl"
                    
                    if os.path.exists(prediction_file):
                        # 读取最后一行（最终预判）
                        with open(prediction_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            if lines:
                                last_prediction = json.loads(lines[-1].strip())
                                signal = last_prediction.get('signal', '')
                                
                                if signal == "低吸":
                                    print(f"✅ 今日预判信号为【低吸】，开始二级触发分析...")
                                    
                                    # 获取2点后的三根柱子
                                    after_2am_data = fetch_after_2am_bars()
                                    
                                    if after_2am_data['success']:
                                        bars = after_2am_data['bars']
                                        bar_details = after_2am_data['bar_details']
                                        
                                        print(f"\n📊 2点后前三根柱子:")
                                        for i, detail in enumerate(bar_details, 1):
                                            color_emoji = {
                                                'green': '🟢',
                                                'red': '🔴',
                                                'yellow': '🟡',
                                                'blank': '⚪'
                                            }.get(detail['color'], '⚪')
                                            print(f"  柱子{i}: {color_emoji} {detail['color']} (上涨占比: {detail['up_ratio']:.1f}%, 时间: {detail['time']})")
                                        
                                        # 分析二级触发
                                        trigger_result = analyze_second_trigger(bars)
                                        
                                        print(f"\n🎯 二级触发结果:")
                                        print(f"  触发状态: {'✅ 已触发' if trigger_result['triggered'] else '⭕ 未触发'}")
                                        print(f"  操作建议: {trigger_result.get('action', '无') or '无'}")
                                        print(f"  描述: {trigger_result['description']}")
                                        
                                        # 更新预判数据，添加二级触发信息
                                        last_prediction['second_trigger'] = {
                                            'checked_at': now_beijing.strftime('%Y-%m-%d %H:%M:%S'),
                                            'bars': bars,
                                            'bar_details': bar_details,
                                            'triggered': trigger_result['triggered'],
                                            'action': trigger_result.get('action'),
                                            'description': trigger_result['description'],
                                            'detail': trigger_result.get('detail')
                                        }
                                        
                                        # 重新保存最后一行
                                        lines[-1] = json.dumps(last_prediction, ensure_ascii=False) + '\n'
                                        with open(prediction_file, 'w', encoding='utf-8') as f:
                                            f.writelines(lines)
                                        
                                        print(f"💾 二级触发信息已保存到: {prediction_file}")
                                        
                                        # 发送Telegram通知
                                        if trigger_result['triggered']:
                                            action_text = {
                                                'immediate_long': '🚀 立即做多',
                                                'wait_dip_then_long': '⏳ 等待大跌后做多'
                                            }.get(trigger_result['action'], '未知')
                                            
                                            # 柱子颜色emoji
                                            color_emojis = []
                                            for detail in bar_details:
                                                emoji = {
                                                    'green': '🟢',
                                                    'red': '🔴',
                                                    'yellow': '🟡',
                                                    'blank': '⚪'
                                                }.get(detail['color'], '⚪')
                                                color_emojis.append(emoji)
                                            
                                            message = f"""
🔔 <b>【低吸】二级触发通知</b> 🔔

📅 日期: {now_beijing.strftime('%Y-%m-%d')}
⏰ 时间: {now_beijing.strftime('%H:%M')} (北京时间)

━━━━━━━━━━━━━━━━━━━━

📊 <b>今日预判: 低吸</b>

🔍 <b>2点后前三根柱子:</b>
{color_emojis[0]} 2:10 - 上涨占比 {bar_details[0]['up_ratio']:.1f}%
{color_emojis[1]} 2:20 - 上涨占比 {bar_details[1]['up_ratio']:.1f}%
{color_emojis[2]} 2:30 - 上涨占比 {bar_details[2]['up_ratio']:.1f}%

━━━━━━━━━━━━━━━━━━━━

✅ <b>二级触发: 已触发</b>
💡 <b>操作建议: {action_text}</b>

{trigger_result['description']}

━━━━━━━━━━━━━━━━━━━━

💬 <b>说明:</b>
{trigger_result.get('detail', '按二级触发策略执行')}

⚠️ <b>风险提示:</b> 请结合实际市场情况谨慎决策
"""
                                            send_telegram_message(message.strip())
                                            print(f"📱 已发送二级触发Telegram通知")
                                        else:
                                            print(f"ℹ️ 未触发二级信号，不发送Telegram通知")
                                    else:
                                        print(f"❌ 获取2点后数据失败: {after_2am_data.get('message', '未知错误')}")
                                else:
                                    print(f"ℹ️ 今日预判信号为【{signal}】，非【低吸】信号，跳过二级触发检查")
                            else:
                                print(f"❌ 预判文件为空")
                    else:
                        print(f"❌ 未找到预判文件: {prediction_file}")
                except Exception as e:
                    print(f"❌ 二级触发检查异常: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 二级触发检查完成，等到明天0:10
                next_run = now_beijing.replace(hour=0, minute=10, second=0, microsecond=0) + timedelta(days=1)
                wait_seconds = (next_run - now_beijing).total_seconds()
                print(f"\n✅ 今日二级触发检查完成")
                print(f"⏳ 下次分析时间: {next_run.strftime('%Y-%m-%d %H:%M')} (北京时间)")
                print(f"💤 等待 {wait_seconds/3600:.1f} 小时...")
                time.sleep(min(3600, wait_seconds))
            
            else:
                # 非分析时段，等待到明天0:10（北京时间）
                if current_hour >= 2 or (current_hour == 0 and current_minute < 10):
                    if current_hour >= 2:
                        # 2点后，等到明天0:10
                        next_run = now_beijing.replace(hour=0, minute=10, second=0, microsecond=0) + timedelta(days=1)
                    else:
                        # 0:00-0:09，等到今天0:10
                        next_run = now_beijing.replace(hour=0, minute=10, second=0, microsecond=0)
                    
                    wait_seconds = (next_run - now_beijing).total_seconds()
                    print(f"⏳ 下次分析时间: {next_run.strftime('%Y-%m-%d %H:%M')} (北京时间)")
                    print(f"💤 等待 {wait_seconds/3600:.1f} 小时...")
                    
                    # 每小时检查一次
                    time.sleep(min(3600, wait_seconds))
        
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断，退出监控")
            break
        except Exception as e:
            print(f"❌ 监控异常: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(300)  # 出错后等5分钟

if __name__ == "__main__":
    main()
