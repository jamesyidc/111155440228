#!/usr/bin/env python3
"""
OKX暴跌预警自动止损监控

功能：
1. 每1分钟检查今天是否有暴跌预警
2. 如果有暴跌预警，自动平掉所有多单（Long仓位）
3. 记录所有止损操作到JSONL文件
4. 发送Telegram通知
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time

# 添加项目根目录到sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Telegram配置
from config.telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    """发送Telegram消息"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram消息发送成功")
            return True
        else:
            print(f"⚠️  Telegram消息发送失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram消息发送异常: {e}")
        return False

# 配置
BASE_URL = "http://localhost:9002"
CHECK_INTERVAL = 60  # 检查间隔（秒）
CRASH_WARNING_API = f"{BASE_URL}/api/coin-change-tracker/has-crash-warning-today"
OKX_POSITIONS_API = f"{BASE_URL}/api/okx-trading/current-positions/account_main"
OKX_CLOSE_POSITION_API = f"{BASE_URL}/api/okx-trading/close-position/account_main"

# 数据目录
DATA_DIR = project_root / "data" / "crash_warning_stop_loss"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 状态文件（记录今天是否已经处理过）
STATE_FILE = DATA_DIR / "stop_loss_state.json"

def get_beijing_time():
    """获取北京时间"""
    now_utc = datetime.now(timezone.utc)
    return now_utc + timedelta(hours=8)

def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def save_stop_loss_record(record):
    """保存止损记录到JSONL文件"""
    beijing_time = get_beijing_time()
    date_str = beijing_time.strftime('%Y%m%d')
    
    jsonl_file = DATA_DIR / f"crash_warning_stop_loss_{date_str}.jsonl"
    
    try:
        with open(jsonl_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"✅ 止损记录已保存: {jsonl_file}")
        return True
    except Exception as e:
        print(f"❌ 保存止损记录失败: {e}")
        return False

def check_crash_warning():
    """检查是否有暴跌预警"""
    try:
        response = requests.get(CRASH_WARNING_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') and data.get('has_warning'):
            return True, data
        return False, None
    except Exception as e:
        print(f"❌ 检查暴跌预警失败: {e}")
        return False, None

def get_current_positions():
    """获取当前持仓"""
    try:
        response = requests.get(OKX_POSITIONS_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            positions = data.get('positions', [])
            # 只返回多单（long）仓位
            long_positions = [p for p in positions if p.get('side', '').lower() == 'long']
            return long_positions
        return []
    except Exception as e:
        print(f"❌ 获取持仓失败: {e}")
        return []

def close_position(inst_id):
    """平仓指定币种的所有仓位"""
    try:
        payload = {
            'inst_id': inst_id,
            'side': 'all'  # 平掉所有仓位
        }
        
        response = requests.post(
            OKX_CLOSE_POSITION_API, 
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        return data.get('success', False), data
    except Exception as e:
        print(f"❌ 平仓 {inst_id} 失败: {e}")
        return False, {'error': str(e)}

def send_stop_loss_notification(warning_data, closed_positions, failed_positions):
    """发送止损通知"""
    beijing_time = get_beijing_time()
    date_str = beijing_time.strftime('%Y-%m-%d')
    time_str = beijing_time.strftime('%H:%M:%S')
    
    pattern_name = warning_data.get('latest_warning', {}).get('pattern_name', '暴跌预警')
    warning_count = warning_data.get('warning_count', 0)
    
    # 构建消息
    message = f"""
🚨🚨🚨 <b>暴跌预警自动止损通知</b> 🚨🚨🚨

📅 <b>日期</b>: {date_str}
⏰ <b>时间</b>: {time_str}

⚠️ <b>预警类型</b>: {pattern_name}
📊 <b>预警次数</b>: {warning_count}次

🛑 <b>已平仓多单</b>: {len(closed_positions)}个
"""

    if closed_positions:
        message += "\n✅ <b>成功平仓:</b>\n"
        for pos in closed_positions:
            inst_id = pos.get('inst_id', 'Unknown')
            pos_size = pos.get('pos', 0)
            avg_price = pos.get('avg_px', 0)
            unrealized_pnl = pos.get('upl', 0)
            message += f"  • {inst_id}: {pos_size} 张 @ {avg_price} (盈亏: {unrealized_pnl} USDT)\n"
    
    if failed_positions:
        message += "\n❌ <b>平仓失败:</b>\n"
        for pos in failed_positions:
            inst_id = pos.get('inst_id', 'Unknown')
            error = pos.get('error', 'Unknown error')
            message += f"  • {inst_id}: {error}\n"
    
    message += f"\n💡 <b>说明</b>: 检测到暴跌预警，已自动平掉所有多单以避免进一步损失"
    
    try:
        send_telegram_message(message)
        print("✅ Telegram通知已发送")
    except Exception as e:
        print(f"❌ 发送Telegram通知失败: {e}")

def process_stop_loss():
    """处理止损逻辑"""
    beijing_time = get_beijing_time()
    today_str = beijing_time.strftime('%Y-%m-%d')
    
    # 检查今天是否已经处理过
    state = load_state()
    last_processed_date = state.get('last_processed_date')
    
    if last_processed_date == today_str:
        print(f"ℹ️ 今天（{today_str}）已经处理过暴跌预警止损，跳过")
        return
    
    # 检查是否有暴跌预警
    has_warning, warning_data = check_crash_warning()
    
    if not has_warning:
        print(f"ℹ️ 今天（{today_str}）暂无暴跌预警")
        return
    
    print(f"🚨 检测到暴跌预警！开始自动止损...")
    
    # 获取当前所有多单仓位
    long_positions = get_current_positions()
    
    if not long_positions:
        print("ℹ️ 当前没有多单仓位")
        
        # 记录到状态文件
        state['last_processed_date'] = today_str
        state['processed_at'] = beijing_time.isoformat()
        state['positions_closed'] = 0
        save_state(state)
        
        # 记录到JSONL
        record = {
            'timestamp': beijing_time.isoformat(),
            'date': today_str,
            'warning_data': warning_data,
            'positions_closed': 0,
            'message': '检测到暴跌预警，但当前没有多单仓位'
        }
        save_stop_loss_record(record)
        return
    
    print(f"📊 找到 {len(long_positions)} 个多单仓位，准备平仓...")
    
    # 平掉所有多单
    closed_positions = []
    failed_positions = []
    
    for pos in long_positions:
        inst_id = pos.get('inst_id')
        pos_size = pos.get('pos')
        
        print(f"  ⏳ 正在平仓 {inst_id} ({pos_size}张)...")
        
        success, result = close_position(inst_id)
        
        if success:
            print(f"  ✅ {inst_id} 平仓成功")
            closed_positions.append(pos)
        else:
            print(f"  ❌ {inst_id} 平仓失败: {result.get('error', 'Unknown error')}")
            pos['error'] = result.get('error', 'Unknown error')
            failed_positions.append(pos)
        
        # 避免API限流
        time.sleep(0.5)
    
    # 发送Telegram通知
    send_stop_loss_notification(warning_data, closed_positions, failed_positions)
    
    # 保存状态
    state['last_processed_date'] = today_str
    state['processed_at'] = beijing_time.isoformat()
    state['positions_closed'] = len(closed_positions)
    state['positions_failed'] = len(failed_positions)
    save_state(state)
    
    # 记录到JSONL
    record = {
        'timestamp': beijing_time.isoformat(),
        'date': today_str,
        'warning_data': warning_data,
        'closed_positions': closed_positions,
        'failed_positions': failed_positions,
        'total_closed': len(closed_positions),
        'total_failed': len(failed_positions)
    }
    save_stop_loss_record(record)
    
    print(f"✅ 止损完成：成功 {len(closed_positions)} 个，失败 {len(failed_positions)} 个")

def main():
    """主循环"""
    print("=" * 80)
    print("🚨 OKX暴跌预警自动止损监控启动")
    print("=" * 80)
    print(f"📌 检查间隔: {CHECK_INTERVAL}秒")
    print(f"📌 数据目录: {DATA_DIR}")
    print(f"📌 API地址: {BASE_URL}")
    print("=" * 80)
    
    while True:
        try:
            beijing_time = get_beijing_time()
            print(f"\n[{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}] 开始检查...")
            
            process_stop_loss()
            
            print(f"✅ 检查完成，等待 {CHECK_INTERVAL}秒...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n⚠️ 接收到退出信号，停止监控")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            print(f"⏳ 等待 {CHECK_INTERVAL}秒后重试...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
