#!/usr/bin/env python3
"""
测试爆仓预警监控器
临时添加一条超过1.5亿的测试数据
"""

import json
import sys
import pytz
from datetime import datetime

sys.path.insert(0, '/home/user/webapp/code/source_code')
from panic_daily_manager import PanicDailyManager

BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# 创建测试数据（1小时爆仓金额：180000万 = 1.8亿）
test_data = {
    'record_time': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S'),
    'hour_1_amount': 180000,  # 1.8亿
    'hour_24_amount': 500000,
    'hour_24_people': 25.5,
    'panic_index': 0.85,
    'wash_index': 15.6,
    'total_position': 80.5
}

print(f"📝 准备写入测试数据...")
print(f"💰 1小时爆仓金额: {test_data['hour_1_amount'] / 10000:.2f}亿")
print(f"⏰ 时间: {test_data['record_time']}")

manager = PanicDailyManager()
success = manager.write_panic_record(test_data)

if success:
    print("✅ 测试数据写入成功")
    print("📢 监控器将在下次检查时（30分钟周期内）发现此数据并发送告警")
    print("🔍 你可以手动触发检查: python3 liquidation_alert_monitor.py")
else:
    print("❌ 测试数据写入失败")
