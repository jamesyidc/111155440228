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

def determine_market_signal(color_counts):
    """
    根据颜色分布判断市场信号
    
    情况1: 有绿+有红+无黄 → 低吸
    情况2: 有绿+有红+有黄 → 等待新低
    情况3: 只有红色 或 红色+空白且空白占比>=25% → 做空
    情况3.1: 红色+空白且空白占比<25% → 诱空试盘抄底（合并自原情况5）
    情况4: 全部绿色 → 诱多不参与
    情况5: 全部为空白 → 空头强控盘，建议观望
    情况6: 红色+黄色（无绿色） → 观望
    情况7: 只有绿色+黄色（无红色） → 等待新低
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
    
    # 情况3 + 3.1: 只有红色（或红色+空白）的判断（无绿色、无黄色）
    if red > 0 and green == 0 and yellow == 0:
        # 情况3.1: 红色+空白且空白占比<25% → 诱空试盘抄底
        if blank > 0 and blank_ratio < 25:
            return "诱空试盘抄底", f"🔴⚪ 红色+空白且空白占比{blank_ratio:.1f}%<25%，诱空行情，可以试盘抄底。操作提示：低点做多"
        # 情况3: 纯红色 或 红色+空白占比>=25% → 做空
        elif blank == 0:
            return "做空", "🔴 只有红色柱子，预判下跌行情，建议做空。操作提示：相对高点做空"
        else:  # blank_ratio >= 25
            return "做空", f"🔴⚪ 红色+空白且空白占比{blank_ratio:.1f}%>=25%，预判下跌行情，建议做空。操作提示：相对高点做空"
    
    # 情况1: 有绿+有红+无黄（低吸）
    if green > 0 and red > 0 and yellow == 0:
        return "低吸", "🟢🔴 有绿有红无黄，红色区间为低吸机会。操作提示：低点做多"
    
    # 情况2: 有绿+有红+有黄（等待新低）
    if green > 0 and red > 0 and yellow > 0:
        return "等待新低", "🟢🔴🟡 有绿有红有黄，可能还有新低，建议等待。操作提示：高点做空"
    
    # 情况7: 红色+黄色（无绿色）→ 观望
    # 必须满足：有红色、有黄色、没有绿色
    if red > 0 and yellow > 0 and green == 0:
        return "观望", "🔴🟡 红色柱子+黄色柱子，没有绿色柱子，多空博弈方向不明。操作提示：无，不参与"
    
    # 情况8: 只有绿色+黄色（无红色）→ 等待新低
    # 必须满足：有绿色、有黄色、没有红色
    if green > 0 and yellow > 0 and red == 0:
        return "等待新低", "🟢🟡 只有绿色和黄色，可能还有新低，建议等待。操作提示：高点做空"
    
    # 其他情况
    return "观望", "⚪ 柱状图混合分布，建议观望"

def save_prediction_data(color_counts, signal, description, is_temp=False):
    """保存预判数据到JSONL文件（按日期分文件）
    
    Args:
        color_counts: 颜色统计
        signal: 预判信号
        description: 描述
        is_temp: 是否为临时数据（0-2点之间）
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
    
    # 保存预判数据
    save_prediction_data(color_counts, signal, description, is_temp=is_temp)
    
    # 只在2:00发送Telegram消息（最终预判）
    if is_final:
        # 构建Telegram消息
        blank_info = f"⚪ 空白: {color_counts.get('blank', 0)}根 (上涨占比 = 0%, 占比: {color_counts.get('blank_ratio', 0):.1f}%)\n" if color_counts.get('blank', 0) > 0 else ""
        
        message = f"""
<b>🔔 币种走势预判 - {now.strftime('%Y-%m-%d %H:%M')}</b>

<b>📊 柱状图颜色统计 (0-2点):</b>
🟢 绿色: {color_counts['green']}根 (上涨占比 &gt; 55%)
🔴 红色: {color_counts['red']}根 (上涨占比 &lt; 45%)
🟡 黄色: {color_counts['yellow']}根 (45% ≤ 占比 ≤ 55%)
{blank_info}
<b>🎯 预判信号: {signal}</b>
{description}

<b>📖 分析规则:</b>
• 情况1: 有绿+有红+无黄 → 低吸机会
• 情况2: 有绿+有红+有黄 → 等待新低
• 情况3: 纯红色 或 红色+空白占比&gt;=25% → 做空信号
• 情况3.1: 红色+空白占比&lt;25% → 诱空试盘抄底
• 情况4: 全部绿色 → 诱多不参与
• 情况5: 全部为空白 → 空头强控盘，建议观望
• 情况6: 红色+黄色（无绿色） → 观望，不参与
• 情况7: 绿色+黄色（无红色） → 等待新低

⏰ 分析时段: 0:10 - 2:00
📈 数据来源: 10分钟上涨占比（共12根柱子）
"""
        
        # 发送Telegram消息
        send_telegram_message(message.strip())
        print(f"📱 已发送Telegram通知")
    else:
        print(f"⏰ 当前 {now.strftime('%H:%M')}，临时数据保存，不发送Telegram")
    
    print(f"\n✅ 分析完成")

def main():
    """主函数 - 持续监控"""
    print("🚀 币种涨跌预判监控器启动")
    print("⏰ 监控时段: 每天 0:10 - 2:00 (北京时间)")
    print("📊 分析指标: 10分钟上涨占比")
    print("🔄 更新频率: 每10分钟（0:10, 0:20, 0:30, ..., 1:50, 2:00）")
    
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
            
            if current_hour == 0 and current_minute >= 10:
                in_analysis_period = True  # 0:10 - 0:59
            elif current_hour == 1:
                in_analysis_period = True  # 1:00 - 1:59
            elif current_hour == 2 and current_minute == 0:
                in_analysis_period = True  # 2:00 整点（最终预判）
            
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
                if next_hour >= 2 and next_minute > 0:
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
