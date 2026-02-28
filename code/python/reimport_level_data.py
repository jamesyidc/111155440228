#!/usr/bin/env python3
"""
重新导入level类型的历史数据
从每秒级的币种详细数据聚合为每分钟级的汇总数据
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import pytz

# 配置
DATA_DIR = Path("/home/user/webapp/data/support_resistance_daily")
DB_PATH = "/home/user/webapp/price_position_v2/config/data/db/price_position.db"
JSONL_OUTPUT_DIR = Path("/home/user/webapp/price_position_v2/data/timeline_jsonl")

# 时区
BJ_TZ = pytz.timezone('Asia/Shanghai')

def process_level_records(jsonl_file, target_date):
    """
    处理level类型记录，聚合为每分钟数据
    
    Args:
        jsonl_file: 原始JSONL文件路径
        target_date: 目标日期 (YYYY-MM-DD)
    
    Returns:
        list: 每分钟聚合后的数据点列表
    """
    print(f"📂 处理文件: {jsonl_file}")
    
    # 按分钟分组
    minute_groups = defaultdict(list)
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                
                # 只处理level类型
                if record.get('type') != 'level':
                    continue
                
                # 提取data字段（币种详细数据）
                data = record.get('data', {})
                if not data:
                    continue
                
                # 获取时间戳（从record或data中）
                record_time = data.get('record_time_beijing') or data.get('record_time') or record.get('timestamp')
                if not record_time:
                    continue
                
                # 解析时间，向下取整到分钟
                if 'T' in record_time:
                    dt = datetime.fromisoformat(record_time.replace('T', ' ').replace('Z', ''))
                else:
                    dt = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                
                minute_key = dt.replace(second=0).strftime('%Y-%m-%d %H:%M:00')
                
                # 添加到对应分钟组（存储data字段）
                minute_groups[minute_key].append(data)
                
            except Exception as e:
                print(f"⚠️  行 {line_num} 解析失败: {e}")
                continue
    
    print(f"✅ 共读取 {sum(len(v) for v in minute_groups.values())} 条level记录")
    print(f"✅ 聚合为 {len(minute_groups)} 个分钟级数据点")
    
    # 聚合每分钟的数据
    minute_data = []
    
    for minute_time in sorted(minute_groups.keys()):
        records = minute_groups[minute_time]
        
        # 统计各类币种数量
        support_48h_count = 0
        support_7d_count = 0
        pressure_48h_count = 0
        pressure_7d_count = 0
        
        support_48h_symbols = []
        support_7d_symbols = []
        pressure_48h_symbols = []
        pressure_7d_symbols = []
        
        for rec in records:
            symbol = rec.get('symbol', '')
            
            # 支撑线1 (48小时)
            dist_support_48h = rec.get('distance_to_support_1', 100)
            if dist_support_48h <= 5:
                support_48h_count += 1
                support_48h_symbols.append(symbol)
            
            # 支撑线2 (7天)
            dist_support_7d = rec.get('distance_to_support_2', 100)
            if dist_support_7d <= 5:
                support_7d_count += 1
                support_7d_symbols.append(symbol)
            
            # 压力线1 (48小时)
            position_48h = rec.get('position_48h', 0)
            if position_48h >= 95:
                pressure_48h_count += 1
                pressure_48h_symbols.append(symbol)
            
            # 压力线2 (7天)
            position_7d = rec.get('position_7d', 0)
            if position_7d >= 95:
                pressure_7d_count += 1
                pressure_7d_symbols.append(symbol)
        
        # 判定信号类型
        signal_type = 'none'
        signal_triggered = 0
        trigger_reason = ''
        
        # 抄底信号
        if (support_48h_count >= 1 and 
            support_7d_count >= 1 and 
            support_48h_count + support_7d_count >= 20):
            signal_type = 'buy'
            signal_triggered = 1
            trigger_reason = f'支撑线1={support_48h_count}, 支撑线2={support_7d_count}, 总和={support_48h_count + support_7d_count}'
        
        # 逃顶信号
        elif (pressure_48h_count >= 1 and 
              pressure_7d_count >= 1 and 
              pressure_48h_count + pressure_7d_count >= 8):
            signal_type = 'sell'
            signal_triggered = 1
            trigger_reason = f'压力线1={pressure_48h_count}, 压力线2={pressure_7d_count}, 总和={pressure_48h_count + pressure_7d_count}'
        
        # 构建数据点
        data_point = {
            'snapshot_time': minute_time,
            'support_line_48h': support_48h_count,
            'support_line_7d': support_7d_count,
            'pressure_line_48h': pressure_48h_count,
            'pressure_line_7d': pressure_7d_count,
            'signal_type': signal_type,
            'signal_triggered': signal_triggered,
            'trigger_reason': trigger_reason,
            'detail_data': {
                'support_48h_symbols': support_48h_symbols,
                'support_7d_symbols': support_7d_symbols,
                'pressure_48h_symbols': pressure_48h_symbols,
                'pressure_7d_symbols': pressure_7d_symbols
            }
        }
        
        minute_data.append(data_point)
    
    return minute_data


def write_to_database(data_points, target_date):
    """
    将数据点写入数据库
    
    Args:
        data_points: 数据点列表
        target_date: 目标日期
    """
    if not data_points:
        print(f"⚠️  {target_date}: 无数据点，跳过")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 先删除该日期的旧数据
    cursor.execute("""
        DELETE FROM signal_timeline 
        WHERE date(snapshot_time) = ?
    """, (target_date,))
    
    deleted_count = cursor.rowcount
    print(f"🗑️  删除 {target_date} 的旧数据: {deleted_count} 条")
    
    # 插入新数据
    inserted_count = 0
    
    for point in data_points:
        try:
            cursor.execute("""
                INSERT INTO signal_timeline (
                    snapshot_time,
                    support_line_48h,
                    support_line_7d,
                    pressure_line_48h,
                    pressure_line_7d,
                    signal_type,
                    signal_triggered,
                    trigger_reason,
                    detail_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                point['snapshot_time'],
                point['support_line_48h'],
                point['support_line_7d'],
                point['pressure_line_48h'],
                point['pressure_line_7d'],
                point['signal_type'],
                point['signal_triggered'],
                point['trigger_reason'],
                json.dumps(point['detail_data'], ensure_ascii=False)
            ))
            inserted_count += 1
        except Exception as e:
            print(f"⚠️  插入失败 {point['snapshot_time']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {target_date}: 插入 {inserted_count} 条新数据")


def write_to_jsonl(data_points, target_date):
    """
    将数据点写入JSONL文件
    
    Args:
        data_points: 数据点列表
        target_date: 目标日期
    """
    if not data_points:
        return
    
    JSONL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = JSONL_OUTPUT_DIR / f"{target_date}.jsonl"
    
    # 备份现有文件
    if output_file.exists():
        backup_file = output_file.with_suffix('.jsonl.backup')
        output_file.rename(backup_file)
        print(f"📦 备份旧文件: {backup_file}")
    
    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for point in data_points:
            f.write(json.dumps(point, ensure_ascii=False) + '\n')
    
    print(f"💾 写入JSONL: {output_file} ({len(data_points)} 条)")


def main():
    """
    主函数：处理所有历史日期
    """
    print("=" * 80)
    print("🚀 开始重新导入level类型历史数据")
    print("=" * 80)
    
    # 获取所有JSONL文件
    jsonl_files = sorted(DATA_DIR.glob("support_resistance_*.jsonl"))
    
    print(f"\n📊 找到 {len(jsonl_files)} 个历史文件")
    
    total_files = 0
    total_points = 0
    
    for jsonl_file in jsonl_files:
        # 从文件名提取日期
        filename = jsonl_file.stem  # support_resistance_20260121
        date_str = filename.split('_')[-1]  # 20260121
        
        try:
            target_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        except:
            print(f"⚠️  无法解析日期: {filename}")
            continue
        
        print(f"\n" + "=" * 80)
        print(f"📅 处理日期: {target_date}")
        print("=" * 80)
        
        # 处理level记录
        data_points = process_level_records(jsonl_file, target_date)
        
        if not data_points:
            print(f"⚠️  {target_date}: 无有效数据点")
            continue
        
        # 写入数据库
        write_to_database(data_points, target_date)
        
        # 写入JSONL
        write_to_jsonl(data_points, target_date)
        
        total_files += 1
        total_points += len(data_points)
        
        print(f"✅ {target_date}: 完成")
    
    print("\n" + "=" * 80)
    print("🎉 全部导入完成!")
    print("=" * 80)
    print(f"📊 处理文件数: {total_files}")
    print(f"📊 总数据点数: {total_points}")
    print(f"📊 平均每文件: {total_points // total_files if total_files > 0 else 0} 个数据点")
    print("=" * 80)


if __name__ == '__main__':
    main()
