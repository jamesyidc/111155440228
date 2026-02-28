#!/usr/bin/env python3
"""
数据迁移脚本：从老系统导入基础时间轴数据到新系统

只导入基础数据（4条线的币种数量），其他统计由新系统自动计算
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

class DataMigration:
    def __init__(self):
        # 老系统数据路径
        self.old_data_path = Path('/home/user/webapp/data/support_resistance_daily')
        
        # 新系统数据库路径
        self.new_db_path = Path('/home/user/webapp/price_position_v2/config/data/db/price_position.db')
        
        # 字段映射
        self.field_mapping = {
            'scenario_1_count': 'support_48h',
            'scenario_2_count': 'support_7d',
            'scenario_3_count': 'pressure_48h',
            'scenario_4_count': 'pressure_7d'
        }
    
    def load_old_data(self, date_str):
        """
        从老系统JSONL加载指定日期的数据
        date_str: YYYY-MM-DD格式
        """
        # 转换为文件名格式：YYYYMMDD
        file_date = date_str.replace('-', '')
        file_path = self.old_data_path / f'support_resistance_{file_date}.jsonl'
        
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return []
        
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    
                    # 只处理snapshot类型的记录
                    if data.get('type') != 'snapshot':
                        continue
                    
                    snapshot_data = data['data']
                    
                    # 使用北京时间
                    snapshot_time = snapshot_data.get('snapshot_time_beijing') or snapshot_data.get('snapshot_time')
                    
                    # 跳过没有时间戳的记录
                    if not snapshot_time:
                        continue
                    
                    # 转换字段名
                    record = {
                        'snapshot_time': snapshot_time,
                        'support_48h': snapshot_data.get('scenario_1_count', 0),
                        'support_7d': snapshot_data.get('scenario_2_count', 0),
                        'pressure_48h': snapshot_data.get('scenario_3_count', 0),
                        'pressure_7d': snapshot_data.get('scenario_4_count', 0)
                    }
                    
                    records.append(record)
                    
                except Exception as e:
                    print(f"⚠️ 第{line_num}行解析错误: {e}")
                    continue
        
        print(f"✅ 从 {file_path.name} 读取 {len(records)} 条记录")
        return records
    
    def import_to_signal_timeline(self, records):
        """导入数据到 signal_timeline 表"""
        if not records:
            print("⚠️ 没有数据需要导入")
            return 0
        
        conn = sqlite3.connect(self.new_db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        skipped_count = 0
        
        for record in records:
            try:
                # 检查是否已存在
                cursor.execute("""
                    SELECT COUNT(*) FROM signal_timeline 
                    WHERE snapshot_time = ?
                """, (record['snapshot_time'],))
                
                if cursor.fetchone()[0] > 0:
                    skipped_count += 1
                    continue
                
                # 插入基础数据
                # 注意：signal_type 和 signal_triggered 由后端采集器计算
                # 这里只导入基础的4条线数据，设置为默认值
                cursor.execute("""
                    INSERT INTO signal_timeline (
                        snapshot_time,
                        support_line_48h,
                        support_line_7d,
                        pressure_line_48h,
                        pressure_line_7d,
                        signal_type,
                        signal_triggered
                    ) VALUES (?, ?, ?, ?, ?, 'none', 0)
                """, (
                    record['snapshot_time'],
                    record['support_48h'],
                    record['support_7d'],
                    record['pressure_48h'],
                    record['pressure_7d']
                ))
                
                imported_count += 1
                
            except Exception as e:
                print(f"❌ 插入错误: {record['snapshot_time']} - {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ 导入完成: {imported_count} 条新记录, {skipped_count} 条已存在（跳过）")
        return imported_count
    
    def migrate_date(self, date_str):
        """迁移指定日期的数据"""
        print(f"\n{'='*60}")
        print(f"开始迁移日期: {date_str}")
        print(f"{'='*60}")
        
        # 1. 从老系统加载数据
        records = self.load_old_data(date_str)
        
        if not records:
            print(f"⚠️ {date_str} 没有可用数据")
            return False
        
        # 显示数据范围
        times = [r['snapshot_time'] for r in records]
        print(f"📊 时间范围: {times[0]} ~ {times[-1]}")
        print(f"📊 数据统计:")
        print(f"   - 总记录数: {len(records)}")
        
        # 2. 导入到新系统
        imported = self.import_to_signal_timeline(records)
        
        return imported > 0
    
    def verify_import(self, date_str):
        """验证导入的数据"""
        print(f"\n{'='*60}")
        print(f"验证导入数据: {date_str}")
        print(f"{'='*60}")
        
        conn = sqlite3.connect(self.new_db_path)
        cursor = conn.cursor()
        
        # 统计导入的数据
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                MIN(snapshot_time) as first_time,
                MAX(snapshot_time) as last_time
            FROM signal_timeline
            WHERE DATE(snapshot_time) = ?
        """, (date_str,))
        
        result = cursor.fetchone()
        
        print(f"✅ 数据库中的记录:")
        print(f"   - 总数: {result[0]}")
        print(f"   - 第一条: {result[1]}")
        print(f"   - 最后一条: {result[2]}")
        
        # 查看前5条和后5条
        cursor.execute("""
            SELECT snapshot_time, support_line_48h, support_line_7d, pressure_line_48h, pressure_line_7d
            FROM signal_timeline
            WHERE DATE(snapshot_time) = ?
            ORDER BY snapshot_time
            LIMIT 5
        """, (date_str,))
        
        print(f"\n前5条数据:")
        for row in cursor.fetchall():
            print(f"   {row[0]}: 支撑48h={row[1]}, 支撑7d={row[2]}, 压力48h={row[3]}, 压力7d={row[4]}")
        
        cursor.execute("""
            SELECT snapshot_time, support_line_48h, support_line_7d, pressure_line_48h, pressure_line_7d
            FROM signal_timeline
            WHERE DATE(snapshot_time) = ?
            ORDER BY snapshot_time DESC
            LIMIT 5
        """, (date_str,))
        
        print(f"\n后5条数据:")
        for row in cursor.fetchall():
            print(f"   {row[0]}: 支撑48h={row[1]}, 支撑7d={row[2]}, 压力48h={row[3]}, 压力7d={row[4]}")
        
        conn.close()

def main():
    """主函数"""
    print("="*60)
    print("数据迁移脚本：老系统 → 新系统")
    print("只导入基础时间轴数据（4条线的币种数量）")
    print("="*60)
    
    # 要迁移的日期 - 导入有丰富数据的日期
    test_dates = [
        '2026-01-28',  # 2330条非零记录
        '2026-01-29',  # 1306条非零记录
        '2026-01-31',  # 1210条非零记录
        '2026-02-01',  # 101条非零记录
        '2026-02-02',  # 384条非零记录
    ]
    
    migrator = DataMigration()
    
    success_count = 0
    for date_str in test_dates:
        try:
            if migrator.migrate_date(date_str):
                success_count += 1
                migrator.verify_import(date_str)
        except Exception as e:
            print(f"❌ 迁移 {date_str} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"迁移完成: {success_count}/{len(test_dates)} 个日期成功")
    print(f"{'='*60}")
    
    return success_count == len(test_dates)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
