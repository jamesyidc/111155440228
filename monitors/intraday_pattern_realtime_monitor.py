#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日内模式实时监控器 - 每10分钟检测最新的4根柱子
检测到的模式（满足和不满足条件的）都写入JSONL
只有满足条件的才发送TG通知
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 项目根目录
BASE_DIR = Path('/home/user/webapp')
sys.path.insert(0, str(BASE_DIR))

# 数据目录
DATA_DIR = BASE_DIR / 'data' / 'intraday_patterns'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# API基础URL
API_BASE = 'http://localhost:9002'

# 配置
CHECK_INTERVAL = 600  # 检查间隔（秒）= 10分钟
MONITOR_START_HOUR = 2  # 监控开始时间（北京时间）
MONITOR_END_HOUR = 23  # 监控结束时间（北京时间）

# Telegram配置
TELEGRAM_BOT_TOKEN = "8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0"
TELEGRAM_CHAT_ID = "-1003227444260"


def log(message):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)


def get_beijing_time():
    """获取北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_time = utc_now + timedelta(hours=8)
    return beijing_time


def send_telegram(message, retries=3):
    """发送Telegram消息"""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }, timeout=10)
            
            if response.status_code == 200:
                log(f'✅ TG消息发送成功')
                return True
            else:
                log(f'⚠️ TG消息发送失败 (尝试 {attempt + 1}/{retries}): HTTP {response.status_code}')
        except Exception as e:
            log(f'❌ TG消息发送异常 (尝试 {attempt + 1}/{retries}): {e}')
        
        if attempt < retries - 1:
            time.sleep(2)
    
    return False


def get_latest_bars(count=4):
    """获取最新的N根10分钟柱子数据"""
    try:
        # 从coin_change_tracker获取今天的数据
        beijing_time = get_beijing_time()
        date_str = beijing_time.strftime('%Y%m%d')
        
        # 读取今日JSONL数据
        data_file = BASE_DIR / 'data' / 'coin_change_tracker' / f'coin_change_{date_str}.jsonl'
        
        if not data_file.exists():
            log(f'⚠️ 数据文件不存在: {data_file}')
            return None, None, None
        
        # 读取所有记录
        records = []
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        
        if not records:
            log('⚠️ 今日数据为空')
            return None, None, None
        
        # 计算10分钟柱子
        bars = []
        current_time = beijing_time.replace(hour=2, minute=0, second=0, microsecond=0)
        end_time = beijing_time.replace(hour=23, minute=59, second=0, microsecond=0)
        
        while current_time < end_time:
            target_time_str = current_time.strftime('%H:%M')
            
            # 收集这个10分钟内的记录
            interval_records = []
            for r in records:
                time_str = r.get('beijing_time') or r.get('time', '')
                if not time_str:
                    continue
                
                try:
                    if ' ' in time_str:
                        time_part = time_str.split()[1]
                    else:
                        time_part = time_str
                    
                    hour, minute, *_ = map(int, time_part.split(':'))
                    
                    if hour == current_time.hour and minute >= current_time.minute and minute < current_time.minute + 10:
                        interval_records.append(r)
                except:
                    continue
            
            # 计算上涨占比
            up_ratio = 0
            if interval_records:
                up_count = sum(1 for r in interval_records if r.get('total_change', 0) > 0)
                up_ratio = (up_count / len(interval_records)) * 100
            
            # 确定颜色
            if up_ratio == 0:
                color = 'blank'
                emoji = '⚪'
            elif up_ratio > 55:
                color = 'green'
                emoji = '🟢'
            elif up_ratio >= 45:
                color = 'yellow'
                emoji = '🟡'
            else:
                color = 'red'
                emoji = '🔴'
            
            bars.append({
                'time': target_time_str,
                'up_ratio': round(up_ratio, 2),
                'color': color,
                'emoji': emoji
            })
            
            current_time += timedelta(minutes=10)
        
        # 获取最新的N根柱子
        latest_bars = bars[-count:] if len(bars) >= count else bars
        
        # 获取当日总涨跌幅
        total_change = records[-1].get('total_change', 0)
        
        # 获取当日预判
        daily_prediction = get_daily_prediction()
        
        return latest_bars, total_change, daily_prediction
        
    except Exception as e:
        log(f'❌ 获取最新柱子数据失败: {e}')
        return None, None, None


def get_daily_prediction():
    """获取今日预判"""
    try:
        beijing_time = get_beijing_time()
        date_str = beijing_time.strftime('%Y-%m-%d')
        
        prediction_file = BASE_DIR / 'data' / 'daily_predictions' / f'prediction_{date_str}.json'
        if prediction_file.exists():
            with open(prediction_file, 'r', encoding='utf-8') as f:
                pred_data = json.load(f)
                return pred_data.get('signal', '')
    except:
        pass
    return None


def check_pattern_1(bars, daily_prediction):
    """检查模式1：诱多等待新低"""
    if len(bars) < 3:
        return []
    
    # 确定阈值
    threshold = 65 if daily_prediction and '等待新低' in daily_prediction else 50
    
    detected_patterns = []
    
    # 检查4根柱子模式：红→黄→黄→绿
    if len(bars) >= 4:
        colors = [bars[-4]['color'], bars[-3]['color'], bars[-2]['color'], bars[-1]['color']]
        if colors == ['red', 'yellow', 'yellow', 'green']:
            trigger_ratio = bars[-1]['up_ratio']
            detected_patterns.append({
                'pattern_type': 'pattern_1_4',
                'pattern_name': '诱多等待新低',
                'bar_type': '红→黄→黄→绿 (4根)',
                'signal': '预高做空',
                'time_range': f"{bars[-4]['time']}-{bars[-1]['time']}",
                'bars': [
                    {'time': bars[-4]['time'], 'up_ratio': bars[-4]['up_ratio'], 'color': '红', 'emoji': '🔴'},
                    {'time': bars[-3]['time'], 'up_ratio': bars[-3]['up_ratio'], 'color': '黄', 'emoji': '🟡'},
                    {'time': bars[-2]['time'], 'up_ratio': bars[-2]['up_ratio'], 'color': '黄', 'emoji': '🟡'},
                    {'time': bars[-1]['time'], 'up_ratio': bars[-1]['up_ratio'], 'color': '绿', 'emoji': '🟢'}
                ],
                'trigger_ratio': trigger_ratio,
                'threshold': threshold,
                'satisfied': trigger_ratio >= threshold
            })
    
    # 检查3根柱子模式：红→黄→绿
    if len(bars) >= 3:
        colors = [bars[-3]['color'], bars[-2]['color'], bars[-1]['color']]
        if colors == ['red', 'yellow', 'green']:
            trigger_ratio = bars[-1]['up_ratio']
            detected_patterns.append({
                'pattern_type': 'pattern_1_3',
                'pattern_name': '诱多等待新低',
                'bar_type': '红→黄→绿 (3根)',
                'signal': '预高做空',
                'time_range': f"{bars[-3]['time']}-{bars[-1]['time']}",
                'bars': [
                    {'time': bars[-3]['time'], 'up_ratio': bars[-3]['up_ratio'], 'color': '红', 'emoji': '🔴'},
                    {'time': bars[-2]['time'], 'up_ratio': bars[-2]['up_ratio'], 'color': '黄', 'emoji': '🟡'},
                    {'time': bars[-1]['time'], 'up_ratio': bars[-1]['up_ratio'], 'color': '绿', 'emoji': '🟢'}
                ],
                'trigger_ratio': trigger_ratio,
                'threshold': threshold,
                'satisfied': trigger_ratio >= threshold
            })
        
        # 绿→黄→红
        elif colors == ['green', 'yellow', 'red']:
            trigger_ratio = bars[-1]['up_ratio']
            detected_patterns.append({
                'pattern_type': 'pattern_1_3',
                'pattern_name': '诱多等待新低',
                'bar_type': '绿→黄→红 (3根)',
                'signal': '预高做空',
                'time_range': f"{bars[-3]['time']}-{bars[-1]['time']}",
                'bars': [
                    {'time': bars[-3]['time'], 'up_ratio': bars[-3]['up_ratio'], 'color': '绿', 'emoji': '🟢'},
                    {'time': bars[-2]['time'], 'up_ratio': bars[-2]['up_ratio'], 'color': '黄', 'emoji': '🟡'},
                    {'time': bars[-1]['time'], 'up_ratio': bars[-1]['up_ratio'], 'color': '红', 'emoji': '🔴'}
                ],
                'trigger_ratio': trigger_ratio,
                'threshold': threshold,
                'satisfied': trigger_ratio >= threshold
            })
    
    return detected_patterns


def check_pattern_3(bars, total_change):
    """检查模式3：筑底信号"""
    if len(bars) < 3:
        return []
    
    detected_patterns = []
    colors = [bars[-3]['color'], bars[-2]['color'], bars[-1]['color']]
    
    if colors == ['yellow', 'green', 'yellow']:
        trigger_ratio = bars[-1]['up_ratio']
        satisfied = trigger_ratio < 10 and total_change < -50
        
        detected_patterns.append({
            'pattern_type': 'pattern_3',
            'pattern_name': '筑底信号',
            'bar_type': '黄→绿→黄 (3根)',
            'signal': '预低做多',
            'time_range': f"{bars[-3]['time']}-{bars[-1]['time']}",
            'bars': [
                {'time': bars[-3]['time'], 'up_ratio': bars[-3]['up_ratio'], 'color': '黄', 'emoji': '🟡'},
                {'time': bars[-2]['time'], 'up_ratio': bars[-2]['up_ratio'], 'color': '绿', 'emoji': '🟢'},
                {'time': bars[-1]['time'], 'up_ratio': bars[-1]['up_ratio'], 'color': '黄', 'emoji': '🟡'}
            ],
            'trigger_ratio': trigger_ratio,
            'threshold': 10.0,
            'total_change': total_change,
            'satisfied': satisfied,
            'failure_reasons': []
        })
        
        if not satisfied:
            if trigger_ratio >= 10:
                detected_patterns[-1]['failure_reasons'].append(f'最后一根柱子上涨占比 {trigger_ratio:.2f}% >= 10.00% (需要 < 10.00%)')
            if total_change >= -50:
                detected_patterns[-1]['failure_reasons'].append(f'当日涨跌幅总和 {total_change:.2f}% >= -50.00% (需要 < -50.00%)')
    
    return detected_patterns


def check_pattern_4(bars):
    """检查模式4：诱空信号"""
    if len(bars) < 3:
        return []
    
    detected_patterns = []
    
    # 检查4根柱子：绿→红→红→绿
    if len(bars) >= 4:
        colors = [bars[-4]['color'], bars[-3]['color'], bars[-2]['color'], bars[-1]['color']]
        if colors == ['green', 'red', 'red', 'green']:
            middle_ratios = [bars[-3]['up_ratio'], bars[-2]['up_ratio']]
            satisfied = all(r < 10 for r in middle_ratios)
            
            detected_patterns.append({
                'pattern_type': 'pattern_4_4',
                'pattern_name': '诱空信号',
                'bar_type': '绿→红→红→绿 (4根)',
                'signal': '预低做多',
                'time_range': f"{bars[-4]['time']}-{bars[-1]['time']}",
                'bars': [
                    {'time': bars[-4]['time'], 'up_ratio': bars[-4]['up_ratio'], 'color': '绿', 'emoji': '🟢'},
                    {'time': bars[-3]['time'], 'up_ratio': bars[-3]['up_ratio'], 'color': '红', 'emoji': '🔴'},
                    {'time': bars[-2]['time'], 'up_ratio': bars[-2]['up_ratio'], 'color': '红', 'emoji': '🔴'},
                    {'time': bars[-1]['time'], 'up_ratio': bars[-1]['up_ratio'], 'color': '绿', 'emoji': '🟢'}
                ],
                'trigger_ratio': middle_ratios,
                'threshold': 10.0,
                'satisfied': satisfied,
                'failure_reasons': [] if satisfied else [f'中间红柱子上涨占比 [{", ".join([f"{r:.2f}%" for r in middle_ratios])}] 存在 >= 10.00% 的情况']
            })
    
    # 检查3根柱子：绿→红→绿
    if len(bars) >= 3:
        colors = [bars[-3]['color'], bars[-2]['color'], bars[-1]['color']]
        if colors == ['green', 'red', 'green']:
            middle_ratio = bars[-2]['up_ratio']
            satisfied = middle_ratio < 10
            
            detected_patterns.append({
                'pattern_type': 'pattern_4_3',
                'pattern_name': '诱空信号',
                'bar_type': '绿→红→绿 (3根)',
                'signal': '预低做多',
                'time_range': f"{bars[-3]['time']}-{bars[-1]['time']}",
                'bars': [
                    {'time': bars[-3]['time'], 'up_ratio': bars[-3]['up_ratio'], 'color': '绿', 'emoji': '🟢'},
                    {'time': bars[-2]['time'], 'up_ratio': bars[-2]['up_ratio'], 'color': '红', 'emoji': '🔴'},
                    {'time': bars[-1]['time'], 'up_ratio': bars[-1]['up_ratio'], 'color': '绿', 'emoji': '🟢'}
                ],
                'trigger_ratio': [middle_ratio],
                'threshold': 10.0,
                'satisfied': satisfied,
                'failure_reasons': [] if satisfied else [f'中间红柱子上涨占比 {middle_ratio:.2f}% >= 10.00% (需要 < 10.00%)']
            })
    
    return detected_patterns


def write_to_jsonl(pattern_data):
    """将检测结果追加写入JSONL文件"""
    try:
        beijing_time = get_beijing_time()
        date_str = beijing_time.strftime('%Y-%m-%d')
        
        # JSONL文件路径
        jsonl_file = DATA_DIR / f'all_detections_{date_str}.jsonl'
        
        # 追加写入
        with open(jsonl_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(pattern_data, ensure_ascii=False) + '\n')
        
        log(f'✅ 检测结果已写入JSONL: {jsonl_file}')
        return True
    
    except Exception as e:
        log(f'❌ 写入JSONL失败: {e}')
        return False


def send_pattern_notification(pattern):
    """发送模式检测通知（满足条件的才发送）"""
    if not pattern.get('satisfied'):
        return False
    
    # 构建TG消息
    bars_str = ' → '.join([f"{b['emoji']} {b['time']} ({b['up_ratio']}%)" for b in pattern['bars']])
    
    message = f"""
🔔 <b>日内模式触发</b>

📊 模式: {pattern['pattern_name']}
🎯 类型: {pattern['bar_type']}
⏰ 时间: {pattern['time_range']}
📈 信号: {pattern['signal']}

📌 柱子序列:
{bars_str}

✅ 触发占比: {pattern['trigger_ratio']if isinstance(pattern['trigger_ratio'], list) else f"{pattern['trigger_ratio']:.2f}"}%
🎚️ 阈值: {pattern['threshold']}%

<i>检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
    
    # 发送3次
    success_count = 0
    for i in range(3):
        if send_telegram(message.strip()):
            success_count += 1
        time.sleep(1)
    
    log(f'📤 TG通知发送完成: {success_count}/3')
    return success_count > 0


def monitor_loop():
    """监控主循环"""
    log('=' * 80)
    log('🚀 日内模式实时监控器启动')
    log('📊 监控时间: 每天 2:00 - 23:59')
    log('⏰ 检查间隔: 10分钟')
    log('=' * 80)
    
    # 用于去重
    last_detection_time = None
    
    while True:
        try:
            beijing_time = get_beijing_time()
            current_hour = beijing_time.hour
            
            # 检查是否在监控时间内
            if current_hour < MONITOR_START_HOUR or current_hour >= MONITOR_END_HOUR:
                log(f'⏸️ 当前时间 {beijing_time.strftime("%H:%M")} 不在监控时间内，休眠...')
                time.sleep(300)  # 休眠5分钟
                continue
            
            log(f'\n{"=" * 80}')
            log(f'🔍 开始检测... ({beijing_time.strftime("%Y-%m-%d %H:%M:%S")})')
            
            # 获取最新的4根柱子
            latest_bars, total_change, daily_prediction = get_latest_bars(count=4)
            
            if not latest_bars:
                log('⚠️ 未获取到柱子数据，跳过本次检测')
                time.sleep(CHECK_INTERVAL)
                continue
            
            log(f'📊 最新柱子: {len(latest_bars)}根')
            log(f'📈 总涨跌幅: {total_change:.2f}%')
            log(f'🎯 大周期预判: {daily_prediction or "未知"}')
            
            # 显示最新柱子
            for bar in latest_bars:
                log(f'   {bar["emoji"]} {bar["time"]} - {bar["up_ratio"]}%')
            
            # 检测所有模式
            all_patterns = []
            
            # 模式1: 诱多等待新低
            patterns_1 = check_pattern_1(latest_bars, daily_prediction)
            all_patterns.extend(patterns_1)
            
            # 模式3: 筑底信号
            patterns_3 = check_pattern_3(latest_bars, total_change)
            all_patterns.extend(patterns_3)
            
            # 模式4: 诱空信号
            patterns_4 = check_pattern_4(latest_bars)
            all_patterns.extend(patterns_4)
            
            if not all_patterns:
                log('✅ 未检测到任何模式')
            else:
                log(f'\n📋 检测到 {len(all_patterns)} 个模式:')
                
                for i, pattern in enumerate(all_patterns, 1):
                    satisfied = pattern.get('satisfied', False)
                    status = '✅ 满足条件' if satisfied else '⚠️ 不满足条件'
                    
                    log(f'\n  [{i}] {pattern["pattern_name"]} - {status}')
                    log(f'      时间: {pattern["time_range"]}')
                    log(f'      类型: {pattern["bar_type"]}')
                    log(f'      信号: {pattern["signal"]}')
                    
                    if satisfied:
                        # 满足条件: 发送TG通知
                        log(f'      📤 发送TG通知...')
                        send_pattern_notification(pattern)
                    else:
                        # 不满足条件: 只记录原因
                        reasons = pattern.get('failure_reasons', [])
                        if reasons:
                            log(f'      原因:')
                            for reason in reasons:
                                log(f'        - {reason}')
                    
                    # 写入JSONL
                    pattern_data = {
                        'timestamp': beijing_time.isoformat(),
                        'date': beijing_time.strftime('%Y-%m-%d'),
                        'detection_time': beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                        **pattern
                    }
                    write_to_jsonl(pattern_data)
            
            log(f'\n✅ 本次检测完成，等待下次检测...')
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log('\n⏹️ 收到停止信号，退出监控...')
            break
        except Exception as e:
            log(f'❌ 监控异常: {e}')
            import traceback
            traceback.print_exc()
            time.sleep(60)


if __name__ == '__main__':
    monitor_loop()
