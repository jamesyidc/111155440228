#!/usr/bin/env python3
"""
计算信号标记和逃顶统计

功能：
1. 根据支撑/压力线数据计算抄底和逃顶信号
2. 统计24小时和2小时的逃顶信号数量
3. 更新signal_timeline表的signal_type和signal_triggered字段
4. 更新escape_stats_timeline表的统计数据
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

class SignalCalculator:
    def __init__(self):
        self.db_path = Path('/home/user/webapp/price_position_v2/config/data/db/price_position.db')
        
        # 信号判定阈值
        self.BUY_THRESHOLDS = {
            'support_48h_min': 1,
            'support_7d_min': 1,
            'sum_min': 20
        }
        
        self.SELL_THRESHOLDS = {
            'pressure_48h_min': 1,
            'pressure_7d_min': 1,
            'sum_min': 8
        }
    
    def calculate_signal(self, support_48h, support_7d, pressure_48h, pressure_7d):
        """
        判定信号类型
        
        抄底信号条件：
        - 支撑48h >= 1
        - 支撑7d >= 1
        - 支撑48h + 支撑7d >= 20
        
        逃顶信号条件：
        - 压力48h >= 1
        - 压力7d >= 1
        - 压力48h + 压力7d >= 8
        """
        support_sum = support_48h + support_7d
        pressure_sum = pressure_48h + pressure_7d
        
        # 判定抄底信号
        is_buy = (
            support_48h >= self.BUY_THRESHOLDS['support_48h_min'] and
            support_7d >= self.BUY_THRESHOLDS['support_7d_min'] and
            support_sum >= self.BUY_THRESHOLDS['sum_min']
        )
        
        # 判定逃顶信号
        is_sell = (
            pressure_48h >= self.SELL_THRESHOLDS['pressure_48h_min'] and
            pressure_7d >= self.SELL_THRESHOLDS['pressure_7d_min'] and
            pressure_sum >= self.SELL_THRESHOLDS['sum_min']
        )
        
        if is_buy and is_sell:
            # 同时触发，选择更强的信号
            return ('buy', 1) if support_sum > pressure_sum else ('sell', 1)
        elif is_buy:
            return ('buy', 1)
        elif is_sell:
            return ('sell', 1)
        else:
            return ('none', 0)
    
    def update_signals_for_date(self, date_str):
        """更新指定日期的信号标记"""
        print(f"\n{'='*60}")
        print(f"计算信号: {date_str}")
        print(f"{'='*60}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取该日期的所有记录
        cursor.execute("""
            SELECT 
                id, snapshot_time,
                support_line_48h, support_line_7d,
                pressure_line_48h, pressure_line_7d
            FROM signal_timeline
            WHERE DATE(snapshot_time) = ?
            ORDER BY snapshot_time ASC
        """, (date_str,))
        
        records = cursor.fetchall()
        print(f"✅ 读取 {len(records)} 条记录")
        
        buy_count = 0
        sell_count = 0
        updated_count = 0
        
        for record in records:
            record_id, snapshot_time, support_48h, support_7d, pressure_48h, pressure_7d = record
            
            # 计算信号
            signal_type, signal_triggered = self.calculate_signal(
                support_48h, support_7d, pressure_48h, pressure_7d
            )
            
            # 更新数据库
            cursor.execute("""
                UPDATE signal_timeline
                SET signal_type = ?,
                    signal_triggered = ?
                WHERE id = ?
            """, (signal_type, signal_triggered, record_id))
            
            updated_count += 1
            
            if signal_type == 'buy':
                buy_count += 1
            elif signal_type == 'sell':
                sell_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ 更新完成: {updated_count} 条记录")
        print(f"   - 抄底信号: {buy_count} 个")
        print(f"   - 逃顶信号: {sell_count} 个")
        print(f"   - 无信号: {updated_count - buy_count - sell_count} 个")
        
        return buy_count, sell_count
    
    def calculate_escape_stats_for_date(self, date_str):
        """计算指定日期的逃顶统计（24h和2h）"""
        print(f"\n{'='*60}")
        print(f"计算逃顶统计: {date_str}")
        print(f"{'='*60}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取该日期的所有记录
        cursor.execute("""
            SELECT 
                snapshot_time,
                signal_type,
                signal_triggered
            FROM signal_timeline
            WHERE DATE(snapshot_time) = ?
            ORDER BY snapshot_time ASC
        """, (date_str,))
        
        records = cursor.fetchall()
        print(f"✅ 读取 {len(records)} 条记录")
        
        # 清空该日期的旧统计数据
        cursor.execute("""
            DELETE FROM escape_stats_timeline
            WHERE DATE(snapshot_time) = ?
        """, (date_str,))
        
        inserted_count = 0
        
        # 为每条记录计算24h和2h的逃顶统计
        for i, (snapshot_time, signal_type, signal_triggered) in enumerate(records):
            current_time = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S')
            
            # 计算24小时前的时间
            time_24h_ago = current_time - timedelta(hours=24)
            
            # 计算2小时前的时间
            time_2h_ago = current_time - timedelta(hours=2)
            
            # 统计24小时内的逃顶信号数量
            cursor.execute("""
                SELECT COUNT(*)
                FROM signal_timeline
                WHERE signal_type = 'sell'
                AND signal_triggered = 1
                AND snapshot_time >= ?
                AND snapshot_time <= ?
            """, (time_24h_ago.strftime('%Y-%m-%d %H:%M:%S'), snapshot_time))
            
            escape_24h_count = cursor.fetchone()[0]
            
            # 统计2小时内的逃顶信号数量
            cursor.execute("""
                SELECT COUNT(*)
                FROM signal_timeline
                WHERE signal_type = 'sell'
                AND signal_triggered = 1
                AND snapshot_time >= ?
                AND snapshot_time <= ?
            """, (time_2h_ago.strftime('%Y-%m-%d %H:%M:%S'), snapshot_time))
            
            escape_2h_count = cursor.fetchone()[0]
            
            # 插入统计数据
            cursor.execute("""
                INSERT INTO escape_stats_timeline (
                    snapshot_time,
                    escape_24h_count,
                    escape_2h_count
                ) VALUES (?, ?, ?)
            """, (snapshot_time, escape_24h_count, escape_2h_count))
            
            inserted_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ 统计完成: {inserted_count} 条记录")
        
        return inserted_count
    
    def process_all_dates(self):
        """处理数据库中所有日期的数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有有数据的日期
        cursor.execute("""
            SELECT DISTINCT DATE(snapshot_time) as date
            FROM signal_timeline
            ORDER BY date ASC
        """)
        
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"开始处理所有日期")
        print(f"{'='*60}")
        print(f"共 {len(dates)} 个日期需要处理")
        print(f"日期列表: {', '.join(dates)}")
        
        total_buy = 0
        total_sell = 0
        
        for date in dates:
            # 更新信号标记
            buy_count, sell_count = self.update_signals_for_date(date)
            total_buy += buy_count
            total_sell += sell_count
            
            # 计算逃顶统计
            self.calculate_escape_stats_for_date(date)
        
        print(f"\n{'='*60}")
        print(f"✅ 全部处理完成")
        print(f"{'='*60}")
        print(f"总统计:")
        print(f"  - 总抄底信号: {total_buy} 个")
        print(f"  - 总逃顶信号: {total_sell} 个")
        print(f"  - 处理日期数: {len(dates)} 个")


def main():
    calculator = SignalCalculator()
    calculator.process_all_dates()


if __name__ == '__main__':
    main()
