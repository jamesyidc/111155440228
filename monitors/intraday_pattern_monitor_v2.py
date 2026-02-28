#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全时间段日内模式监控器 (2:00-23:59)
v2.0 - 增强版触发条件

核心原则：小周期服从大周期
- 大周期做空（等待新低/做空/诱多不参与/观望）→ 禁止所有做多信号
- 大周期做多（低吸/诱空试仓抄底）→ 禁止所有做空信号

===== 模式定义 =====

情况1: 诱多等待新低 [做空]
  颜色模式：
    - 红→黄→绿
    - 绿→黄→红  
    - 红→黄→黄→绿（新增）
  触发条件：
    - 如果日线预测=等待新低：中间柱子up_ratio > 65%
    - 如果日线预测=做空：中间柱子up_ratio > 50%
    - 如果日线预测=观望：中间柱子up_ratio > 50%
  操作：逢高做空

情况2: 诱空试仓抄底 [做多]
  颜色模式：
    - 红柱后连续3个空白柱子
  触发条件：
    - 空白柱子占当天总数不超过25%
    - 触发后在空白柱子时做多
  操作：开多单试仓

情况3: 筑底信号 [做多]
  颜色模式：
    - 黄→绿→黄
  触发条件：
    - 涨跌幅总和 < -50
    - 触发后中间柱子up_ratio < 10%时做多
  操作：逢低做多

情况4: 诱空信号 [做多]
  颜色模式：
    - 绿→红→红→绿（4根）
    - 绿→红→绿（3根）
  触发条件：
    - 触发后中间柱子up_ratio < 10%时做多
  操作：逢低可以做多

颜色定义:
- 绿色: up_ratio > 55%
- 黄色: 45% ≤ up_ratio ≤ 55%
- 红色: up_ratio < 45%
- 空白: up_ratio = 0%
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import deque

# 项目根目录
BASE_DIR = Path('/home/user/webapp')
sys.path.insert(0, str(BASE_DIR))

# 数据目录
DATA_DIR = BASE_DIR / 'data' / 'intraday_patterns'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# API基础URL
API_BASE = 'http://localhost:9002'

# 配置
CHECK_INTERVAL = 600  # 10分钟检查一次
MONITOR_START_HOUR = 2
MONITOR_END_HOUR = 23
BLANK_RATIO_THRESHOLD = 0.25  # 空白占比阈值25%

# Telegram配置
TELEGRAM_BOT_TOKEN = "8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0"
TELEGRAM_CHAT_ID = "-1003227444260"


def log(message):
    """打印日志"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def get_beijing_time():
    """获取北京时间"""
    return datetime.now(timezone.utc) + timedelta(hours=8)


def get_daily_prediction():
    """获取今日0-2点预判信号"""
    try:
        url = f'{API_BASE}/api/coin-change-tracker/daily-prediction'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('success') and result.get('data'):
            signal = result['data'].get('signal', '')
            log(f"✅ 今日预判: {signal}")
            return {
                'signal': signal,
                'description': result['data'].get('description', ''),
                'date': get_beijing_time().strftime('%Y-%m-%d')
            }
        else:
            log("⚠️ 无预判数据，允许所有信号")
            return None
    except Exception as e:
        log(f"❌ 获取预判失败: {e}")
        return None


def get_color(up_ratio):
    """根据上涨占比判断颜色"""
    if up_ratio == 0:
        return '空白'
    elif up_ratio > 55:
        return '绿色'
    elif up_ratio >= 45:
        return '黄色'
    else:
        return '红色'


def get_current_total_change():
    """获取当前总涨跌幅"""
    try:
        url = f'{API_BASE}/api/coin-change-tracker/latest'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('success') and 'total_change' in result:
            return result['total_change']
        return 0
    except:
        return 0


def fetch_up_ratio_bars():
    """获取今日10分钟上涨占比柱状图数据"""
    try:
        url = f'{API_BASE}/api/coin-change-tracker/up-ratio-bars'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('success') and 'bars' in result:
            bars = result['bars']
            log(f"📊 获取到{len(bars)}根柱子数据")
            return bars
        else:
            log("⚠️ 无柱子数据")
            return []
    except Exception as e:
        log(f"❌ 获取柱子数据失败: {e}")
        return []


def is_signal_allowed(signal_type, daily_prediction):
    """判断信号是否被大周期允许
    
    Args:
        signal_type: 'short' 或 'long'
        daily_prediction: 大周期预判数据
    
    Returns:
        (allowed: bool, reason: str)
    """
    if not daily_prediction:
        return True, "无预判数据"
    
    signal = daily_prediction['signal']
    
    # 做空信号组：等待新低、做空、诱多不参与、观望
    short_signals = ['等待新低', '做空', '诱多不参与', '观望']
    # 做多信号组：低吸、诱空试仓抄底
    long_signals = ['低吸', '诱空试仓抄底']
    
    # 大周期做空，禁止做多
    if any(s in signal for s in short_signals):
        if signal_type == 'long':
            return False, f"大周期{signal}禁止做多"
    
    # 大周期做多，禁止做空
    if any(s in signal for s in long_signals):
        if signal_type == 'short':
            return False, f"大周期{signal}禁止做空"
    
    return True, f"大周期{signal}允许"


def check_pattern1(bars, daily_prediction):
    """情况1: 诱多等待新低
    
    颜色模式：
      - 红→黄→绿
      - 绿→黄→红
      - 红→黄→黄→绿（新增）
    
    触发条件：
      - 如果日线=等待新低：中间柱子up_ratio > 65%
      - 如果日线=做空：中间柱子up_ratio > 50%
      - 如果日线=观望：中间柱子up_ratio > 50%
    """
    detections = []
    
    # 检测3根模式：红→黄→绿 或 绿→黄→红
    for i in range(len(bars) - 2):
        b1, b2, b3 = bars[i], bars[i+1], bars[i+2]
        c1, c2, c3 = b1['color'], b2['color'], b3['color']
        
        if (c1 == '红色' and c2 == '黄色' and c3 == '绿色') or \
           (c1 == '绿色' and c2 == '黄色' and c3 == '红色'):
            
            # 判断触发条件
            middle_up_ratio = b2['up_ratio']
            threshold = get_pattern1_threshold(daily_prediction)
            
            if middle_up_ratio > threshold:
                detections.append({
                    'pattern': '情况1',
                    'name': '诱多等待新低',
                    'type': f'{c1}→{c2}→{c3}',
                    'signal_type': 'short',
                    'operation': '逢高做空',
                    'time_range': f"{b1['time']}-{b3['time']}",
                    'bars': [b1, b2, b3],
                    'trigger_condition': f"中间柱up_ratio={middle_up_ratio:.1f}% > {threshold}%"
                })
    
    # 检测4根模式：红→黄→黄→绿（新增）
    for i in range(len(bars) - 3):
        b1, b2, b3, b4 = bars[i], bars[i+1], bars[i+2], bars[i+3]
        c1, c2, c3, c4 = b1['color'], b2['color'], b3['color'], b4['color']
        
        if c1 == '红色' and c2 == '黄色' and c3 == '黄色' and c4 == '绿色':
            # 取两个黄色柱子的平均值
            middle_avg = (b2['up_ratio'] + b3['up_ratio']) / 2
            threshold = get_pattern1_threshold(daily_prediction)
            
            if middle_avg > threshold:
                detections.append({
                    'pattern': '情况1',
                    'name': '诱多等待新低',
                    'type': '红→黄→黄→绿',
                    'signal_type': 'short',
                    'operation': '逢高做空',
                    'time_range': f"{b1['time']}-{b4['time']}",
                    'bars': [b1, b2, b3, b4],
                    'trigger_condition': f"中间柱avg={middle_avg:.1f}% > {threshold}%"
                })
    
    return detections


def get_pattern1_threshold(daily_prediction):
    """获取情况1的触发阈值"""
    if not daily_prediction:
        return 50  # 默认50%
    
    signal = daily_prediction['signal']
    
    if '等待新低' in signal:
        return 65
    elif '做空' in signal or '观望' in signal:
        return 50
    else:
        return 50


def check_pattern2(bars):
    """情况2: 诱空试仓抄底
    
    颜色模式：红柱后连续3个空白柱子
    触发条件：空白柱子占当天总数≤25%
    """
    detections = []
    total_bars = len(bars)
    blank_count = sum(1 for b in bars if b['color'] == '空白')
    blank_ratio = blank_count / total_bars if total_bars > 0 else 0
    
    if blank_ratio > BLANK_RATIO_THRESHOLD:
        log(f"⚠️ 空白占比{blank_ratio*100:.1f}%超过25%，跳过情况2检测")
        return []
    
    for i in range(len(bars) - 3):
        b1, b2, b3, b4 = bars[i], bars[i+1], bars[i+2], bars[i+3]
        
        if (b1['color'] == '红色' and 
            b2['color'] == '空白' and 
            b3['color'] == '空白' and 
            b4['color'] == '空白'):
            
            detections.append({
                'pattern': '情况2',
                'name': '诱空试仓抄底',
                'type': '红+3空白',
                'signal_type': 'long',
                'operation': '开多单试仓',
                'time_range': f"{b1['time']}-{b4['time']}",
                'bars': [b1, b2, b3, b4],
                'trigger_condition': f"空白占比{blank_ratio*100:.1f}% ≤ 25%，在空白柱做多"
            })
    
    return detections


def check_pattern3(bars, total_change):
    """情况3: 筑底信号
    
    颜色模式：黄→绿→黄
    触发条件：
      - 涨跌幅总和 < -50
      - 触发后中间柱up_ratio < 10%时做多
    """
    detections = []
    
    if total_change >= -50:
        log(f"⚠️ 总涨跌幅{total_change:.1f}% ≥ -50，跳过情况3检测")
        return []
    
    for i in range(len(bars) - 2):
        b1, b2, b3 = bars[i], bars[i+1], bars[i+2]
        
        if (b1['color'] == '黄色' and 
            b2['color'] == '绿色' and 
            b3['color'] == '黄色'):
            
            middle_up_ratio = b2['up_ratio']
            
            if middle_up_ratio < 10:
                detections.append({
                    'pattern': '情况3',
                    'name': '筑底信号',
                    'type': '黄→绿→黄',
                    'signal_type': 'long',
                    'operation': '逢低做多',
                    'time_range': f"{b1['time']}-{b3['time']}",
                    'bars': [b1, b2, b3],
                    'trigger_condition': f"总涨跌幅{total_change:.1f}% < -50，中间柱{middle_up_ratio:.1f}% < 10%"
                })
    
    return detections


def check_pattern4(bars):
    """情况4: 诱空信号
    
    颜色模式：
      - 绿→红→红→绿（4根）
      - 绿→红→绿（3根）
    触发条件：触发后中间柱up_ratio < 10%时做多
    """
    detections = []
    
    # 检测4根模式
    for i in range(len(bars) - 3):
        b1, b2, b3, b4 = bars[i], bars[i+1], bars[i+2], bars[i+3]
        
        if (b1['color'] == '绿色' and 
            b2['color'] == '红色' and 
            b3['color'] == '红色' and 
            b4['color'] == '绿色'):
            
            middle_avg = (b2['up_ratio'] + b3['up_ratio']) / 2
            
            if middle_avg < 10:
                detections.append({
                    'pattern': '情况4',
                    'name': '诱空信号',
                    'type': '绿→红→红→绿',
                    'signal_type': 'long',
                    'operation': '逢低可以做多',
                    'time_range': f"{b1['time']}-{b4['time']}",
                    'bars': [b1, b2, b3, b4],
                    'trigger_condition': f"中间柱avg={middle_avg:.1f}% < 10%"
                })
    
    # 检测3根模式
    for i in range(len(bars) - 2):
        b1, b2, b3 = bars[i], bars[i+1], bars[i+2]
        
        if (b1['color'] == '绿色' and 
            b2['color'] == '红色' and 
            b3['color'] == '绿色'):
            
            middle_up_ratio = b2['up_ratio']
            
            if middle_up_ratio < 10:
                detections.append({
                    'pattern': '情况4',
                    'name': '诱空信号',
                    'type': '绿→红→绿',
                    'signal_type': 'long',
                    'operation': '逢低可以做多',
                    'time_range': f"{b1['time']}-{b3['time']}",
                    'bars': [b1, b2, b3],
                    'trigger_condition': f"中间柱{middle_up_ratio:.1f}% < 10%"
                })
    
    return detections


def send_telegram(message):
    """发送Telegram通知"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            log("✅ Telegram通知已发送")
            return True
        else:
            log(f"❌ Telegram发送失败: {response.text}")
            return False
    except Exception as e:
        log(f"❌ Telegram发送异常: {e}")
        return False


def save_detection(detection, daily_prediction):
    """保存检测记录"""
    try:
        beijing_time = get_beijing_time()
        date_str = beijing_time.strftime('%Y%m%d')
        
        record = {
            'timestamp': beijing_time.isoformat(),
            'date': date_str,
            'daily_prediction': daily_prediction['signal'] if daily_prediction else None,
            **detection
        }
        
        file_path = DATA_DIR / f'detections_{date_str}.jsonl'
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        log(f"💾 记录已保存: {file_path.name}")
    except Exception as e:
        log(f"❌ 保存记录失败: {e}")


def format_telegram_message(detection, allowed, reason):
    """格式化Telegram消息"""
    status = "✅ 触发" if allowed else "❌ 阻止"
    msg = f"<b>{status} {detection['pattern']} {detection['name']}</b>\n\n"
    msg += f"<b>模式</b>: {detection['type']}\n"
    msg += f"<b>时间</b>: {detection['time_range']}\n"
    msg += f"<b>操作</b>: {detection['operation']}\n"
    msg += f"<b>触发条件</b>: {detection['trigger_condition']}\n"
    
    if not allowed:
        msg += f"\n⚠️ <b>阻止原因</b>: {reason}\n"
    
    msg += f"\n⏰ {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')}"
    return msg


def monitor_loop():
    """监控主循环"""
    log("🚀 启动日内模式监控器")
    log(f"⏰ 监控时间: {MONITOR_START_HOUR}:00 - {MONITOR_END_HOUR}:59")
    log(f"🔄 检查间隔: {CHECK_INTERVAL}秒")
    
    while True:
        try:
            beijing_time = get_beijing_time()
            hour = beijing_time.hour
            
            # 检查是否在监控时间内
            if hour < MONITOR_START_HOUR or hour > MONITOR_END_HOUR:
                log(f"⏸️ 当前{hour}:00不在监控时间内，等待...")
                time.sleep(300)  # 5分钟后再检查
                continue
            
            log(f"\n{'='*60}")
            log(f"🔍 开始检测 {beijing_time.strftime('%H:%M:%S')}")
            log(f"{'='*60}")
            
            # 1. 获取大周期预判
            daily_prediction = get_daily_prediction()
            
            # 2. 获取当前总涨跌幅
            total_change = get_current_total_change()
            log(f"📊 当前总涨跌幅: {total_change:.2f}%")
            
            # 3. 获取柱子数据
            bars = fetch_up_ratio_bars()
            if not bars:
                log("⚠️ 无柱子数据，跳过本次检测")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # 4. 检测所有模式
            all_detections = []
            
            # 情况1
            pattern1 = check_pattern1(bars, daily_prediction)
            all_detections.extend(pattern1)
            
            # 情况2
            pattern2 = check_pattern2(bars)
            all_detections.extend(pattern2)
            
            # 情况3
            pattern3 = check_pattern3(bars, total_change)
            all_detections.extend(pattern3)
            
            # 情况4
            pattern4 = check_pattern4(bars)
            all_detections.extend(pattern4)
            
            log(f"📋 检测结果: 共{len(all_detections)}个模式")
            
            # 5. 过滤并处理检测结果
            for detection in all_detections:
                signal_type = detection['signal_type']
                allowed, reason = is_signal_allowed(signal_type, daily_prediction)
                
                log(f"\n{detection['pattern']} {detection['name']}")
                log(f"  模式: {detection['type']}")
                log(f"  时间: {detection['time_range']}")
                log(f"  操作: {detection['operation']}")
                log(f"  {'✅ 允许' if allowed else '❌ 阻止'}: {reason}")
                
                if allowed:
                    # 保存记录
                    save_detection(detection, daily_prediction)
                    
                    # 发送通知
                    message = format_telegram_message(detection, allowed, reason)
                    send_telegram(message)
            
            if not all_detections:
                log("✅ 本次检测未发现模式触发")
            
            log(f"\n{'='*60}")
            log(f"⏰ 下次检测: {(beijing_time + timedelta(seconds=CHECK_INTERVAL)).strftime('%H:%M:%S')}")
            log(f"{'='*60}\n")
            
            # 等待下次检测
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("\n⚠️ 收到中断信号，停止监控")
            break
        except Exception as e:
            log(f"\n❌ 监控异常: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)  # 等待1分钟后重试


if __name__ == '__main__':
    monitor_loop()
