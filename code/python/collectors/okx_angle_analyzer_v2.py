#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX趋势角度分析器 V2
分析趋势图中的锐角和钝角形态（基于视觉角度）
"""

import json
import os
import math
from datetime import datetime, timedelta
from collections import defaultdict

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
COIN_TRACKER_DIR = os.path.join(DATA_DIR, 'coin_change_tracker')
OUTPUT_DIR = os.path.join(DATA_DIR, 'okx_angle_analysis')

# 图表参数（用于计算视觉角度）
CHART_WIDTH_PX = 800  # 图表宽度（像素）
CHART_HEIGHT_PX = 400  # 图表高度（像素）
CHART_TIME_RANGE_MIN = 600  # 时间范围（分钟，10小时）
CHART_PRICE_RANGE_PCT = 100  # 价格范围（%，-20到+80）

def load_trend_data(date_str):
    """加载指定日期的趋势数据（从coin_change_tracker）"""
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
                    data_points.append({
                        'time': item['time'],
                        'cumulative_pct': float(item.get('total_change', 0)),
                        'timestamp': item.get('timestamp', '')
                    })
                except Exception as e:
                    continue
    
    data_points.sort(key=lambda x: x['time'])
    return data_points

def parse_time_to_minutes(time_str):
    """将时间字符串转换为分钟数"""
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 60 + m + s / 60.0
    except:
        return 0

def find_peak_and_valley(data_points, start_idx=0):
    """找到最高点A和其后的回升点C"""
    if len(data_points) < 3:
        return None
    
    peak_idx = start_idx
    peak_value = data_points[start_idx]['cumulative_pct']
    
    for i in range(start_idx, len(data_points)):
        if data_points[i]['cumulative_pct'] > peak_value:
            peak_value = data_points[i]['cumulative_pct']
            peak_idx = i
    
    if peak_idx == len(data_points) - 1:
        return None
    
    valley_idx = None
    min_value = peak_value
    
    for i in range(peak_idx + 1, len(data_points)):
        current = data_points[i]['cumulative_pct']
        
        if current < min_value:
            min_value = current
            valley_idx = i
        elif valley_idx is not None and current > data_points[valley_idx]['cumulative_pct']:
            break
    
    if valley_idx is None or valley_idx == peak_idx + 1:
        return None
    
    return (peak_idx, valley_idx)

def find_price_match_before_peak(data_points, peak_idx, valley_price):
    """在最高点A之前，找到与谷底C价格相等（或最接近）的点C'"""
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
    
    if min_diff > 5.0:
        return None
    
    return best_idx

def calculate_angle_visual(data_points, c_prime_idx, peak_idx):
    """
    计算视觉角度（基于图表像素比例）
    
    公式：angle = arctan((price_diff_px) / (time_diff_px))
    """
    # 价格差（%）
    price_diff_pct = data_points[peak_idx]['cumulative_pct'] - data_points[c_prime_idx]['cumulative_pct']
    
    # 时间差（分钟）
    time_peak = parse_time_to_minutes(data_points[peak_idx]['time'])
    time_c_prime = parse_time_to_minutes(data_points[c_prime_idx]['time'])
    time_diff_min = time_peak - time_c_prime
    
    if time_diff_min <= 0:
        return None
    
    # 转换为像素
    price_diff_px = (price_diff_pct / CHART_PRICE_RANGE_PCT) * CHART_HEIGHT_PX
    time_diff_px = (time_diff_min / CHART_TIME_RANGE_MIN) * CHART_WIDTH_PX
    
    # 计算角度
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
        'valley_time': '',  # 将在外部设置
        'valley_price': 0
    }

def analyze_angles_by_hour(data_points):
    """按小时分析角度，每小时只保留最大的一个角度"""
    angles_by_hour = defaultdict(list)
    processed_peaks = set()
    
    idx = 0
    while idx < len(data_points):
        result = find_peak_and_valley(data_points, idx)
        
        if result is None:
            idx += 1
            continue
        
        peak_idx, valley_idx = result
        
        if peak_idx in processed_peaks:
            idx += 1
            continue
        
        processed_peaks.add(peak_idx)
        
        valley_price = data_points[valley_idx]['cumulative_pct']
        c_prime_idx = find_price_match_before_peak(data_points, peak_idx, valley_price)
        
        if c_prime_idx is None:
            idx = peak_idx + 1
            continue
        
        angle_info = calculate_angle_visual(data_points, c_prime_idx, peak_idx)
        
        if angle_info is None:
            idx = peak_idx + 1
            continue
        
        angle_info['valley_time'] = data_points[valley_idx]['time']
        angle_info['valley_price'] = data_points[valley_idx]['cumulative_pct']
        
        hour = data_points[peak_idx]['time'].split(':')[0]
        angles_by_hour[hour].append(angle_info)
        
        idx = valley_idx + 1
    
    result = {}
    for hour, angles in angles_by_hour.items():
        max_angle = max(angles, key=lambda x: abs(x['angle']))
        result[hour] = max_angle
    
    return result

def save_angle_analysis(date_str, angles_by_hour):
    """保存角度分析结果到JSONL文件"""
    output_file = os.path.join(OUTPUT_DIR, f'okx_angles_{date_str}.jsonl')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for hour, angle_info in sorted(angles_by_hour.items()):
            record = {
                'date': date_str,
                'hour': hour,
                **angle_info,
                'analyzed_at': datetime.now().isoformat()
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"✅ 保存分析结果: {output_file}")
    return output_file

def analyze_date(date_str):
    """分析指定日期的角度"""
    print(f"\n{'='*70}")
    print(f"📐 分析日期: {date_str}")
    print(f"{'='*70}")
    print(f"📊 图表参数: {CHART_WIDTH_PX}×{CHART_HEIGHT_PX}px, {CHART_TIME_RANGE_MIN}min, {CHART_PRICE_RANGE_PCT}%")
    
    data_points = load_trend_data(date_str)
    
    if not data_points:
        print(f"❌ 没有数据可分析")
        return None
    
    print(f"📊 加载了 {len(data_points)} 个数据点")
    
    angles_by_hour = analyze_angles_by_hour(data_points)
    
    if not angles_by_hour:
        print(f"❌ 未找到有效的角度形态")
        return None
    
    print(f"\n📈 找到 {len(angles_by_hour)} 个小时的角度形态:")
    print(f"{'='*70}")
    
    for hour, angle_info in sorted(angles_by_hour.items()):
        angle_type_cn = "🔺 锐角" if angle_info['type'] == 'acute' else "🔻 钝角"
        print(f"\n⏰ {hour}:00 - {int(hour) + 1}:00")
        print(f"   类型: {angle_type_cn}")
        print(f"   视觉角度: {angle_info['angle']:.2f}°")
        print(f"   C'点: {angle_info['c_prime_time']} ({angle_info['c_prime_price']:.2f}%)")
        print(f"   A点:  {angle_info['peak_time']} ({angle_info['peak_price']:.2f}%)")
        print(f"   C点:  {angle_info['valley_time']} ({angle_info['valley_price']:.2f}%)")
        print(f"   实际: {angle_info['vertical_distance_pct']:.2f}% / {angle_info['horizontal_distance_min']:.1f}分钟")
        print(f"   像素: {angle_info['vertical_distance_px']:.1f}px / {angle_info['horizontal_distance_px']:.1f}px")
    
    output_file = save_angle_analysis(date_str, angles_by_hour)
    
    print(f"\n{'='*70}")
    print(f"✅ 分析完成")
    print(f"{'='*70}\n")
    
    return output_file

def analyze_recent_days(days=7):
    """分析最近N天的角度"""
    today = datetime.now()
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y%m%d')
        
        try:
            analyze_date(date_str)
        except Exception as e:
            print(f"❌ 分析 {date_str} 时出错: {e}")
            continue

if __name__ == '__main__':
    import sys
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        analyze_date(date_str)
    else:
        print("📐 OKX趋势角度分析器 V2（视觉角度版本）")
        print("=" * 70)
        analyze_recent_days(days=7)
