#!/usr/bin/env python3
"""
1小时爆仓金额超级预警监控
当1小时爆仓金额超过1.5亿时，连续发送3次TG通知
每30分钟检查一次
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# 添加source_code到路径
sys.path.insert(0, '/home/user/webapp/code/source_code')

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# 阈值：1.5亿（单位：万）
ALERT_THRESHOLD = 150000  # 150000万 = 1.5亿

# TG配置
TG_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TG_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# 日志文件
LOG_FILE = '/home/user/webapp/logs/liquidation_alert_monitor.log'
STATE_FILE = '/home/user/webapp/data/liquidation_alert_state.json'

# 创建日志目录
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)


def log(message):
    """记录日志"""
    timestamp = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except Exception as e:
        print(f"写入日志失败: {e}")


def send_telegram_message(message, retry=3):
    """发送Telegram消息（带重试）"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        log("❌ TG配置未设置")
        return False
    
    url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
    
    for attempt in range(retry):
        try:
            response = requests.post(
                url,
                json={
                    'chat_id': TG_CHAT_ID,
                    'text': message,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                log(f"✅ TG消息发送成功 (尝试 {attempt + 1}/{retry})")
                return True
            else:
                log(f"⚠️ TG消息发送失败 (尝试 {attempt + 1}/{retry}): {response.status_code}")
        except Exception as e:
            log(f"❌ TG消息发送异常 (尝试 {attempt + 1}/{retry}): {e}")
        
        if attempt < retry - 1:
            time.sleep(2)  # 重试前等待2秒
    
    return False


def get_latest_liquidation_data():
    """获取最新的1小时爆仓数据"""
    try:
        from panic_daily_manager import PanicDailyManager
        
        manager = PanicDailyManager()
        # 获取最近1条记录
        records = manager.get_latest_records(limit=1, days_back=1)
        
        if not records:
            log("⚠️ 没有获取到爆仓数据")
            return None
        
        record = records[0]
        data = record.get('data', {})
        
        return {
            'record_time': data.get('record_time', ''),
            'hour_1_amount': data.get('hour_1_amount', 0),
            'hour_24_amount': data.get('hour_24_amount', 0),
            'panic_index': data.get('panic_index', 0),
            'wash_index': data.get('wash_index', 0)
        }
        
    except Exception as e:
        log(f"❌ 获取爆仓数据失败: {e}")
        return None


def load_alert_state():
    """加载告警状态"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        log(f"⚠️ 加载告警状态失败: {e}")
    
    return {
        'last_alert_time': None,
        'last_alert_amount': 0,
        'alert_count': 0
    }


def save_alert_state(state):
    """保存告警状态"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"❌ 保存告警状态失败: {e}")


def should_send_alert(current_amount, state):
    """判断是否应该发送告警"""
    # 如果低于阈值，不发送
    if current_amount < ALERT_THRESHOLD:
        return False
    
    # 如果之前没有发送过告警，发送
    if not state.get('last_alert_time'):
        return True
    
    # 获取上次告警时间
    try:
        last_alert_time = datetime.fromisoformat(state['last_alert_time'])
        now = datetime.now(BEIJING_TZ)
        
        # 如果距离上次告警超过30分钟，发送新告警
        if (now - last_alert_time).total_seconds() > 30 * 60:
            return True
        
    except Exception as e:
        log(f"⚠️ 解析上次告警时间失败: {e}")
        return True
    
    return False


def format_amount(amount):
    """格式化金额显示"""
    yi = amount / 10000  # 万 -> 亿
    return f"{yi:.2f}亿"


def send_super_alert(data):
    """发送超级预警（连续3次）"""
    amount = data['hour_1_amount']
    record_time = data['record_time']
    
    amount_str = format_amount(amount)
    hour_24_str = format_amount(data['hour_24_amount'])
    
    message = f"""🚨🚨🚨 <b>爆仓超级预警</b> 🚨🚨🚨

⚠️ <b>1小时爆仓金额已超过1.5亿！</b>

📊 <b>爆仓数据</b>:
💰 1小时爆仓: <b>{amount_str}</b>
💵 24小时爆仓: {hour_24_str}

📈 <b>市场指标</b>:
😱 恐慌指数: {data['panic_index']}
🌊 清洗指数: {data['wash_index']:.2f}

⏰ 时间: {record_time}

⚠️ <b>注意</b>: 市场波动剧烈，请注意风险！

🔗 查看详情: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/liquidation-monthly
"""
    
    log(f"🚨 准备发送超级预警: {amount_str}")
    
    success_count = 0
    # 连续发送3次
    for i in range(3):
        log(f"📤 发送第 {i + 1}/3 次通知...")
        
        if send_telegram_message(message):
            success_count += 1
        
        # 每次发送之间间隔3秒
        if i < 2:
            time.sleep(3)
    
    log(f"✅ 超级预警发送完成: 成功 {success_count}/3 次")
    return success_count > 0


def check_and_alert():
    """检查并发送告警"""
    log("=" * 60)
    log("🔍 开始检查1小时爆仓金额...")
    
    # 获取最新数据
    data = get_latest_liquidation_data()
    if not data:
        log("❌ 无法获取数据，跳过本次检查")
        return
    
    amount = data['hour_1_amount']
    record_time = data['record_time']
    amount_str = format_amount(amount)
    
    log(f"📊 当前1小时爆仓金额: {amount_str} (阈值: 1.5亿)")
    log(f"⏰ 数据时间: {record_time}")
    
    # 加载告警状态
    state = load_alert_state()
    
    # 判断是否需要发送告警
    if should_send_alert(amount, state):
        log(f"🚨 触发超级预警！金额: {amount_str}")
        
        # 发送3次通知
        if send_super_alert(data):
            # 更新告警状态
            state['last_alert_time'] = datetime.now(BEIJING_TZ).isoformat()
            state['last_alert_amount'] = amount
            state['alert_count'] = state.get('alert_count', 0) + 1
            save_alert_state(state)
            
            log(f"✅ 超级预警发送成功！累计告警 {state['alert_count']} 次")
        else:
            log("❌ 超级预警发送失败")
    else:
        if amount >= ALERT_THRESHOLD:
            log(f"⏳ 金额超过阈值，但距离上次告警不足30分钟，跳过本次通知")
        else:
            log(f"✅ 金额正常（{amount_str} < 1.5亿）")
    
    log(f"💤 下次检查: 30分钟后")


def run_monitor():
    """运行监控器"""
    log("=" * 60)
    log("🚀 启动1小时爆仓金额超级预警监控")
    log(f"⏱️  检查间隔: 30分钟")
    log(f"🎯 告警阈值: 1.5亿")
    log(f"📢 通知次数: 3次/告警")
    log("=" * 60)
    
    while True:
        try:
            check_and_alert()
        except Exception as e:
            log(f"❌ 监控异常: {e}")
            import traceback
            log(traceback.format_exc())
        
        # 等待30分钟
        log(f"😴 等待30分钟后再次检查...")
        time.sleep(30 * 60)  # 30分钟


if __name__ == '__main__':
    try:
        run_monitor()
    except KeyboardInterrupt:
        log("⚠️ 监控器被用户中断")
    except Exception as e:
        log(f"❌ 监控器异常退出: {e}")
        import traceback
        log(traceback.format_exc())
