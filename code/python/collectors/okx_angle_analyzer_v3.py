#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX趋势角度分析器 V3 - 增强版
检测所有显著峰值，不限于每小时一个
"""

import json
import os
import math
from datetime import datetime, timedelta
from collections import defaultdict

# 使用绝对路径指向 /home/user/webapp/data
BASE_DIR = '/home/user/webapp'
DATA_DIR = os.path.join(BASE_DIR, 'data')
COIN_TRACKER_DIR = os.path.join(DATA_DIR, 'coin_change_tracker')
OUTPUT_DIR = os.path.join(DATA_DIR, 'okx_angle_analysis')

# 图表参数
CHART_WIDTH_PX = 800
CHART_HEIGHT_PX = 400
CHART_TIME_RANGE_MIN = 600
CHART_PRICE_RANGE_PCT = 100

# 峰值检测参数
MIN_PEAK_VALUE = 5  # 最小峰值（%）- 降低到5%以捕获更多小峰值
MIN_PEAK_DISTANCE = 30  # 最小峰值间距（分钟）
MIN_VALLEY_TIME_GAP = 2  # C点与A点的最小时间间隔（分钟）

def load_trend_data(date_str):
    file_path = os.path.join(COIN_TRACKER_DIR, f'coin_change_{date_str}.jsonl')
    
    if not os.path.exists(file_path):
        print(f"⚠️ 文件不存在: {file_path}")
        return []
    
    data_points = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    item = json.loads(line)
                    # 从beijing_time提取时间部分（HH:MM:SS）
                    beijing_time = item.get('beijing_time', '')
                    time_part = beijing_time.split(' ')[1] if ' ' in beijing_time else '00:00:00'
                    
                    data_points.append({
                        'time': time_part,  # 使用从beijing_time提取的时间
                        'cumulative_pct': float(item.get('total_change', 0)),
                        'timestamp': item.get('timestamp', '')
                    })
                except Exception as e:
                    continue
    
    data_points.sort(key=lambda x: x['time'])
    return data_points

def parse_time_to_minutes(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 60 + m + s / 60.0
    except:
        return 0

def find_all_peaks(data_points):
    """找到所有显著的峰值（正值和负值）"""
    positive_peaks = []  # 正值峰值（局部最大值）
    negative_peaks = []  # 负值峰值（局部最小值）
    
    # 使用滑动窗口找局部最大值和最小值
    window_size = 5  # 前后各5个点
    
    for i in range(window_size, len(data_points) - window_size):
        current_value = data_points[i]['cumulative_pct']
        
        # 检查是否是局部最大值（正峰值）
        is_max_peak = True
        for j in range(i - window_size, i + window_size + 1):
            if j != i and data_points[j]['cumulative_pct'] >= current_value:
                is_max_peak = False
                break
        
        # 检查是否是局部最小值（负峰值）
        is_min_peak = True
        for j in range(i - window_size, i + window_size + 1):
            if j != i and data_points[j]['cumulative_pct'] <= current_value:
                is_min_peak = False
                break
        
        # 检查正峰值（>=5%）
        if is_max_peak and current_value >= MIN_PEAK_VALUE:
            if len(positive_peaks) == 0:
                positive_peaks.append(i)
            else:
                last_peak_time = parse_time_to_minutes(data_points[positive_peaks[-1]]['time'])
                current_time = parse_time_to_minutes(data_points[i]['time'])
                
                if current_time - last_peak_time >= MIN_PEAK_DISTANCE:
                    positive_peaks.append(i)
        
        # 检查负峰值（<=-5%）
        if is_min_peak and current_value <= -MIN_PEAK_VALUE:
            if len(negative_peaks) == 0:
                negative_peaks.append(i)
            else:
                last_peak_time = parse_time_to_minutes(data_points[negative_peaks[-1]]['time'])
                current_time = parse_time_to_minutes(data_points[i]['time'])
                
                if current_time - last_peak_time >= MIN_PEAK_DISTANCE:
                    negative_peaks.append(i)
    
    return positive_peaks, negative_peaks

def find_valley_after_peak(data_points, peak_idx):
    """在峰值后找谷底（C点与A点间隔必须>=MIN_VALLEY_TIME_GAP分钟）"""
    if peak_idx >= len(data_points) - 1:
        return None
    
    valley_idx = None
    min_value = data_points[peak_idx]['cumulative_pct']
    peak_time = parse_time_to_minutes(data_points[peak_idx]['time'])
    
    for i in range(peak_idx + 1, len(data_points)):
        current = data_points[i]['cumulative_pct']
        current_time = parse_time_to_minutes(data_points[i]['time'])
        
        # 检查时间间隔是否>=MIN_VALLEY_TIME_GAP分钟
        time_diff = current_time - peak_time
        if time_diff < MIN_VALLEY_TIME_GAP:  # 小于最小时间间隔，跳过
            continue
        
        if current < min_value:
            min_value = current
            valley_idx = i
        elif valley_idx is not None and current > data_points[valley_idx]['cumulative_pct']:
            break
    
    return valley_idx

def find_recovery_after_trough(data_points, trough_idx):
    """在谷底（负峰值）后找回升点"""
    if trough_idx >= len(data_points) - 1:
        return None
    
    recovery_idx = None
    max_value = data_points[trough_idx]['cumulative_pct']
    trough_time = parse_time_to_minutes(data_points[trough_idx]['time'])
    
    for i in range(trough_idx + 1, len(data_points)):
        current = data_points[i]['cumulative_pct']
        current_time = parse_time_to_minutes(data_points[i]['time'])
        
        # 检查时间间隔是否>=MIN_VALLEY_TIME_GAP分钟
        time_diff = current_time - trough_time
        if time_diff < MIN_VALLEY_TIME_GAP:
            continue
        
        if current > max_value:
            max_value = current
            recovery_idx = i
        elif recovery_idx is not None and current < data_points[recovery_idx]['cumulative_pct']:
            break
    
    return recovery_idx

def find_price_match_before_peak(data_points, peak_idx, valley_price):
    """在峰值前找价格匹配点（C'点）"""
    if peak_idx == 0:
        return None
    
    best_idx = None
    min_diff = float('inf')
    
    for i in range(peak_idx):
        price = data_points[i]['cumulative_pct']
        diff = abs(price - valley_price)
        
        if diff < min_diff:
            min_diff = diff
            best_idx = i
    
    # 放宽价格匹配条件：从5%提高到10%
    # 对于小峰值，谷底价格可能与之前的价格差距较大
    if min_diff > 10.0:
        return None
    
    return best_idx

def calculate_angle_visual(data_points, c_prime_idx, peak_idx):
    price_diff_pct = data_points[peak_idx]['cumulative_pct'] - data_points[c_prime_idx]['cumulative_pct']
    
    time_peak = parse_time_to_minutes(data_points[peak_idx]['time'])
    time_c_prime = parse_time_to_minutes(data_points[c_prime_idx]['time'])
    time_diff_min = time_peak - time_c_prime
    
    if time_diff_min <= 0:
        return None
    
    price_diff_px = (price_diff_pct / CHART_PRICE_RANGE_PCT) * CHART_HEIGHT_PX
    time_diff_px = (time_diff_min / CHART_TIME_RANGE_MIN) * CHART_WIDTH_PX
    
    angle_rad = math.atan(price_diff_px / time_diff_px)
    angle_deg = math.degrees(angle_rad)
    
    return {
        'angle': angle_deg,
        'type': 'acute' if angle_deg < 45 else 'obtuse',
        'vertical_distance_pct': price_diff_pct,
        'horizontal_distance_min': time_diff_min,
        'vertical_distance_px': price_diff_px,
        'horizontal_distance_px': time_diff_px,
        'c_prime_time': data_points[c_prime_idx]['time'],
        'c_prime_price': data_points[c_prime_idx]['cumulative_pct'],
        'peak_time': data_points[peak_idx]['time'],
        'peak_price': data_points[peak_idx]['cumulative_pct'],
        'valley_time': '',
        'valley_price': 0
    }

def calculate_negative_angle_visual(data_points, c_prime_idx, trough_idx):
    """计算负角度（下降趋势的角度）"""
    price_diff_pct = data_points[c_prime_idx]['cumulative_pct'] - data_points[trough_idx]['cumulative_pct']
    
    time_trough = parse_time_to_minutes(data_points[trough_idx]['time'])
    time_c_prime = parse_time_to_minutes(data_points[c_prime_idx]['time'])
    time_diff_min = time_trough - time_c_prime
    
    if time_diff_min <= 0:
        return None
    
    price_diff_px = (price_diff_pct / CHART_PRICE_RANGE_PCT) * CHART_HEIGHT_PX
    time_diff_px = (time_diff_min / CHART_TIME_RANGE_MIN) * CHART_WIDTH_PX
    
    angle_rad = math.atan(price_diff_px / time_diff_px)
    angle_deg = math.degrees(angle_rad)
    
    return {
        'angle': angle_deg,
        'type': 'acute' if angle_deg < 45 else 'obtuse',
        'vertical_distance_pct': price_diff_pct,
        'horizontal_distance_min': time_diff_min,
        'vertical_distance_px': price_diff_px,
        'horizontal_distance_px': time_diff_px,
        'c_prime_time': data_points[c_prime_idx]['time'],
        'c_prime_price': data_points[c_prime_idx]['cumulative_pct'],
        'peak_time': data_points[trough_idx]['time'],
        'peak_price': data_points[trough_idx]['cumulative_pct'],
        'valley_time': '',
        'valley_price': 0
    }

def analyze_all_angles(data_points):
    """分析所有峰值的角度，每小时只保留最高/最低的一个"""
    positive_peaks, negative_peaks = find_all_peaks(data_points)
    
    print(f"🔍 找到 {len(positive_peaks)} 个正峰值, {len(negative_peaks)} 个负峰值")
    
    # 分析正峰值（向上的角度）
    positive_angles = analyze_positive_peaks(data_points, positive_peaks)
    
    # 分析负峰值（向下的角度）
    negative_angles = analyze_negative_peaks(data_points, negative_peaks)
    
    # 合并所有角度
    all_angles = positive_angles + negative_angles
    
    # 按时间排序
    all_angles.sort(key=lambda x: x['peak_time'])
    
    print(f"📊 总共: {len(all_angles)} 个角度 (正:{len(positive_angles)}, 负:{len(negative_angles)})")
    
    return all_angles

def analyze_positive_peaks(data_points, peak_indices):
    """分析正峰值（局部最大值）"""
    # 按小时分组峰值，每小时只保留最高的
    peaks_by_hour = {}
    for peak_idx in peak_indices:
        peak_time = data_points[peak_idx]['time']
        hour = peak_time.split(':')[0]
        peak_value = data_points[peak_idx]['cumulative_pct']
        
        if hour not in peaks_by_hour or peak_value > data_points[peaks_by_hour[hour]]['cumulative_pct']:
            peaks_by_hour[hour] = peak_idx
    
    angles = []
    
    for hour in sorted(peaks_by_hour.keys()):
        peak_idx = peaks_by_hour[hour]
        valley_idx = find_valley_after_peak(data_points, peak_idx)
        
        if valley_idx is None:
            continue
        
        valley_price = data_points[valley_idx]['cumulative_pct']
        c_prime_idx = find_price_match_before_peak(data_points, peak_idx, valley_price)
        
        if c_prime_idx is None:
            continue
        
        angle_info = calculate_angle_visual(data_points, c_prime_idx, peak_idx)
        
        if angle_info is None:
            continue
        
        angle_info['valley_time'] = data_points[valley_idx]['time']
        angle_info['valley_price'] = valley_price
        angle_info['hour'] = hour
        angle_info['direction'] = 'up'  # 标记为向上的角度
        
        angles.append(angle_info)
    
    return angles

def analyze_negative_peaks(data_points, peak_indices):
    """分析负峰值（局部最小值）"""
    # 按小时分组峰值，每小时只保留最低的
    peaks_by_hour = {}
    for peak_idx in peak_indices:
        peak_time = data_points[peak_idx]['time']
        hour = peak_time.split(':')[0]
        peak_value = data_points[peak_idx]['cumulative_pct']
        
        if hour not in peaks_by_hour or peak_value < data_points[peaks_by_hour[hour]]['cumulative_pct']:
            peaks_by_hour[hour] = peak_idx
    
    angles = []
    
    for hour in sorted(peaks_by_hour.keys()):
        peak_idx = peaks_by_hour[hour]
        # 对于负峰值，找回升点（向上的谷底实际上是向上回升的点）
        recovery_idx = find_recovery_after_trough(data_points, peak_idx)
        
        if recovery_idx is None:
            continue
        
        recovery_price = data_points[recovery_idx]['cumulative_pct']
        c_prime_idx = find_price_match_before_peak(data_points, peak_idx, recovery_price)
        
        if c_prime_idx is None:
            continue
        
        # 计算负角度（从C'点到负峰值的下降角度）
        angle_info = calculate_negative_angle_visual(data_points, c_prime_idx, peak_idx)
        
        if angle_info is None:
            continue
        
        angle_info['valley_time'] = data_points[recovery_idx]['time']
        angle_info['valley_price'] = recovery_price
        angle_info['hour'] = hour
        angle_info['direction'] = 'down'  # 标记为向下的角度
        
        angles.append(angle_info)
    
    return angles

def save_angle_analysis(date_str, angles):
    output_file = os.path.join(OUTPUT_DIR, f'okx_angles_{date_str}.jsonl')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for angle_info in angles:
            record = {
                'date': date_str,
                'hour': angle_info.get('hour', '00'),
                **angle_info,
                'analyzed_at': datetime.now().isoformat()
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"✅ 保存分析结果: {output_file}")
    return output_file

def analyze_date(date_str):
    print(f"\n{'='*70}")
    print(f"📐 分析日期: {date_str} (V3增强版)")
    print(f"{'='*70}")
    
    data_points = load_trend_data(date_str)
    
    if not data_points:
        print(f"❌ 没有数据可分析")
        return None
    
    print(f"📊 加载了 {len(data_points)} 个数据点")
    
    angles = analyze_all_angles(data_points)
    
    if not angles:
        print(f"❌ 未找到有效的角度形态")
        return None
    
    print(f"\n📈 找到 {len(angles)} 个角度形态:")
    print(f"{'='*70}")
    
    # 分类统计
    up_acute = sum(1 for a in angles if a.get('direction') == 'up' and a['type'] == 'acute')
    up_obtuse = sum(1 for a in angles if a.get('direction') == 'up' and a['type'] == 'obtuse')
    down_acute = sum(1 for a in angles if a.get('direction') == 'down' and a['type'] == 'acute')
    down_obtuse = sum(1 for a in angles if a.get('direction') == 'down' and a['type'] == 'obtuse')
    
    print(f"↗️ 上升角度: {up_acute + up_obtuse} 个 (🔺锐角:{up_acute}, 🔻钝角:{up_obtuse})")
    print(f"↘️ 下降角度: {down_acute + down_obtuse} 个 (🔺锐角:{down_acute}, 🔻钝角:{down_obtuse})")
    print()
    
    for angle_info in angles:
        direction_icon = "↗️" if angle_info.get('direction') == 'up' else "↘️"
        angle_type_cn = "🔺 锐角" if angle_info['type'] == 'acute' else "🔻 钝角"
        print(f"{direction_icon} {angle_type_cn} {angle_info['angle']:.2f}° - 峰值: {angle_info['peak_time']} ({angle_info['peak_price']:.2f}%)")
    
    output_file = save_angle_analysis(date_str, angles)
    
    print(f"\n{'='*70}")
    print(f"✅ 分析完成")
    print(f"{'='*70}\n")
    
    return output_file

if __name__ == '__main__':
    import sys
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        analyze_date(date_str)
    else:
        print("用法: python3 okx_angle_analyzer_v3.py YYYYMMDD")
