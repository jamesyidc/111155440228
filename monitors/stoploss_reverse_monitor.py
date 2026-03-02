#!/usr/bin/env python3
"""
止损反手开单监控器
- 监控所有账户的止损事件
- 当检测到止损时，根据配置自动反向开仓
- 防重复触发机制
- 自动执行策略（无需人工确认）
- 发送Telegram通知
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Telegram配置
try:
    from config.telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    TELEGRAM_BOT_TOKEN = None
    TELEGRAM_CHAT_ID = None
    print("⚠️ Telegram配置未找到，将跳过TG通知")

# 配置日志
log_dir = project_root / 'data' / 'stoploss_reverse_orders' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / f"monitor_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 配置常量
ACCOUNTS = ['account_main', 'account_fangfang12', 'account_anchor', 
            'account_poit', 'account_poit_main', 'account_dadanini']
CHECK_INTERVAL = 60  # 检查间隔（秒）
SETTINGS_DIR = project_root / 'data' / 'stoploss_reverse_orders'
TRIGGER_EVENTS_DIR = SETTINGS_DIR / 'trigger_events'
CRASH_WARNING_DIR = project_root / 'data' / 'crash_warning_stop_loss'

# API配置
BASE_URL = "http://localhost:9002"

# 确保目录存在
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
TRIGGER_EVENTS_DIR.mkdir(parents=True, exist_ok=True)
CRASH_WARNING_DIR.mkdir(parents=True, exist_ok=True)


def send_telegram_message(message):
    """发送Telegram消息"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ Telegram配置未设置，跳过通知")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Telegram消息发送成功")
            return True
        else:
            logger.warning(f"⚠️ Telegram消息发送失败: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram消息发送异常: {e}")
        return False


def load_reverse_configs(account_id):
    """加载指定账户的止损反手配置"""
    config_file = SETTINGS_DIR / f'{account_id}_stoploss_reverse.jsonl'
    
    if not config_file.exists():
        logger.debug(f"配置文件不存在: {config_file}")
        return []
    
    configs = []
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    config = json.loads(line)
                    configs.append(config)
        
        logger.debug(f"✅ 账户 {account_id} 加载了 {len(configs)} 个止损反手配置")
        return configs
    except Exception as e:
        logger.error(f"❌ 加载配置失败 {account_id}: {e}")
        return []


def update_trigger_permission(account_id, config_id, allow_trigger):
    """更新触发权限"""
    config_file = SETTINGS_DIR / f'{account_id}_stoploss_reverse.jsonl'
    
    if not config_file.exists():
        logger.error(f"配置文件不存在: {config_file}")
        return False
    
    try:
        # 读取所有配置
        configs = []
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    configs.append(json.loads(line))
        
        # 更新指定配置
        updated = False
        for config in configs:
            if config['id'] == config_id:
                config['allow_trigger'] = allow_trigger
                config['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if not allow_trigger:
                    config['last_triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    config['triggered_count'] = config.get('triggered_count', 0) + 1
                updated = True
                break
        
        if not updated:
            logger.error(f"未找到配置 {config_id}")
            return False
        
        # 写回文件
        with open(config_file, 'w', encoding='utf-8') as f:
            for config in configs:
                f.write(json.dumps(config, ensure_ascii=False) + '\n')
        
        logger.info(f"✅ 更新触发权限成功: {account_id}/{config_id} -> allow_trigger={allow_trigger}")
        return True
    
    except Exception as e:
        logger.error(f"❌ 更新触发权限失败: {e}")
        return False


def log_trigger_event(account_id, config_id, config_type, strategy_code, result, stop_loss_info=None):
    """记录触发事件"""
    event_file = TRIGGER_EVENTS_DIR / f"{account_id}_trigger_events_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    event = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'account_id': account_id,
        'config_id': config_id,
        'config_type': config_type,
        'strategy_code': strategy_code,
        'stop_loss_info': stop_loss_info,  # 止损信息
        'result': result,
        'success': result.get('success', False) if isinstance(result, dict) else False
    }
    
    try:
        with open(event_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
        logger.info(f"📝 触发事件已记录: {account_id}/{config_id}")
    except Exception as e:
        logger.error(f"❌ 记录触发事件失败: {e}")


def check_crash_warning_stop_loss(account_id):
    """
    检查暴跌预警止损事件
    读取今天的止损记录文件
    """
    date_str = datetime.now().strftime('%Y%m%d')
    stop_loss_file = CRASH_WARNING_DIR / f"crash_warning_stop_loss_{date_str}.jsonl"
    
    if not stop_loss_file.exists():
        return []
    
    try:
        # 读取今天的所有止损记录
        stop_loss_events = []
        with open(stop_loss_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    # 检查是否是当前账户的止损
                    if record.get('account_id') == account_id:
                        # 检查是否已经处理过（防止重复）
                        if not record.get('reverse_processed', False):
                            stop_loss_events.append(record)
        
        return stop_loss_events
    except Exception as e:
        logger.error(f"❌ 读取止损记录失败: {e}")
        return []


def mark_stop_loss_as_processed(account_id, stop_loss_record):
    """标记止损记录为已处理"""
    date_str = datetime.now().strftime('%Y%m%d')
    stop_loss_file = CRASH_WARNING_DIR / f"crash_warning_stop_loss_{date_str}.jsonl"
    
    if not stop_loss_file.exists():
        return
    
    try:
        # 读取所有记录
        records = []
        with open(stop_loss_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    # 如果是当前处理的记录，标记为已处理
                    if (record.get('account_id') == account_id and 
                        record.get('timestamp') == stop_loss_record.get('timestamp')):
                        record['reverse_processed'] = True
                        record['reverse_processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    records.append(record)
        
        # 写回文件
        with open(stop_loss_file, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        logger.info(f"✅ 止损记录已标记为已处理")
    except Exception as e:
        logger.error(f"❌ 标记止损记录失败: {e}")


def execute_reverse_strategy(account_id, config_type, strategy_code, stop_loss_positions):
    """
    执行反手策略
    根据strategy_code自动执行对应的开仓策略
    """
    logger.info(f"🚀 执行反手策略: {account_id} - {config_type} - {strategy_code}")
    
    try:
        # 根据策略代码调用对应的API
        api_url = f"{BASE_URL}/api/okx-trading/execute-strategy/{account_id}"
        
        payload = {
            'strategy_code': strategy_code,
            'trigger_source': 'stoploss_reverse',
            'stop_loss_info': {
                'positions_closed': len(stop_loss_positions),
                'total_loss': sum([float(p.get('upl', 0)) for p in stop_loss_positions])
            }
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ 策略执行成功: {result}")
            return result
        else:
            logger.error(f"❌ 策略执行失败: HTTP {response.status_code}")
            return {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'message': response.text[:200]
            }
    
    except Exception as e:
        logger.error(f"❌ 执行策略异常: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'strategy_code': strategy_code,
            'account_id': account_id
        }


def send_reverse_notification(account_id, config_type, strategy_code, result, stop_loss_info):
    """发送反手开单通知"""
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 判断是多单止损还是空单止损
    if config_type == 'long_stoploss_reverse':
        direction = "多单止损 → 反手开空"
        emoji = "🔻"
    else:
        direction = "空单止损 → 反手开多"
        emoji = "🔺"
    
    # 策略名称
    strategy_names = {
        'STG_SHORT_TOP8': '涨幅前8名做空',
        'STG_SHORT_BOTTOM8': '涨幅后8名做空',
        'STG_LONG_TOP8': '涨幅前8名做多',
        'STG_LONG_BOTTOM8': '涨幅后8名做多（抄底）'
    }
    strategy_name = strategy_names.get(strategy_code, strategy_code)
    
    # 止损信息
    closed_count = stop_loss_info.get('positions_closed', 0)
    total_loss = stop_loss_info.get('total_loss', 0)
    
    # 构建消息
    message = f"""
🔄🔄🔄 <b>止损反手开单通知</b> 🔄🔄🔄

{emoji} <b>操作类型</b>: {direction}
📅 <b>时间</b>: {time_str}
👤 <b>账户</b>: {account_id}

🛑 <b>止损信息</b>:
  • 平仓数量: {closed_count} 个
  • 总盈亏: {total_loss:.2f} USDT

🎯 <b>反手策略</b>: {strategy_name}
📊 <b>策略代码</b>: {strategy_code}
"""
    
    # 添加执行结果
    if result.get('success'):
        orders = result.get('orders', [])
        message += f"\n✅ <b>执行成功</b>: 开仓 {len(orders)} 个订单\n"
        
        if orders:
            message += "\n📋 <b>开仓详情:</b>\n"
            for order in orders[:5]:  # 只显示前5个
                inst_id = order.get('inst_id', 'Unknown')
                side = order.get('side', 'Unknown')
                size = order.get('size', 0)
                price = order.get('price', 0)
                message += f"  • {inst_id}: {side} {size} 张 @ {price}\n"
            
            if len(orders) > 5:
                message += f"  ... 还有 {len(orders) - 5} 个订单\n"
    else:
        error = result.get('error', 'Unknown error')
        message += f"\n❌ <b>执行失败</b>: {error}\n"
    
    message += f"\n💡 <b>说明</b>: 检测到止损事件，已自动执行反手开仓策略"
    
    # 发送Telegram通知
    send_telegram_message(message)
    
    # 记录到前端通知队列（供弹窗显示）
    save_frontend_notification(account_id, config_type, strategy_code, result, stop_loss_info)


def save_frontend_notification(account_id, config_type, strategy_code, result, stop_loss_info):
    """保存前端通知（供弹窗显示）"""
    notifications_dir = project_root / 'data' / 'frontend_notifications'
    notifications_dir.mkdir(parents=True, exist_ok=True)
    
    notification_file = notifications_dir / f"{account_id}_notifications.jsonl"
    
    notification = {
        'id': f"reverse_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'type': 'stoploss_reverse',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'account_id': account_id,
        'config_type': config_type,
        'strategy_code': strategy_code,
        'result': result,
        'stop_loss_info': stop_loss_info,
        'read': False,
        'auto_close_seconds': 10  # 10秒后自动关闭
    }
    
    try:
        with open(notification_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(notification, ensure_ascii=False) + '\n')
        logger.info(f"📝 前端通知已保存: {notification_file}")
    except Exception as e:
        logger.error(f"❌ 保存前端通知失败: {e}")


def check_account(account_id):
    """检查单个账户的止损反手触发"""
    logger.debug(f"🔍 检查账户: {account_id}")
    
    # 加载配置
    configs = load_reverse_configs(account_id)
    if not configs:
        logger.debug(f"账户 {account_id} 没有配置")
        return
    
    # 检查暴跌预警止损事件
    stop_loss_events = check_crash_warning_stop_loss(account_id)
    if not stop_loss_events:
        logger.debug(f"账户 {account_id} 没有止损事件")
        return
    
    logger.info(f"⚠️ 检测到 {len(stop_loss_events)} 个止损事件: {account_id}")
    
    # 处理每个止损事件
    for stop_loss_record in stop_loss_events:
        # 所有暴跌预警止损的都是多单，所以触发"多单止损反手开空"
        closed_positions = stop_loss_record.get('closed_positions', [])
        
        # 查找对应的反手配置（多单止损反手开空）
        for config in configs:
            if config['type'] == 'long_stoploss_reverse':
                if not config.get('enabled', False):
                    logger.debug(f"配置未启用: {config['id']}")
                    continue
                
                if not config.get('allow_trigger', True):
                    logger.debug(f"触发权限已禁用: {config['id']}")
                    continue
                
                strategy_code = config.get('target_strategy_code')
                if not strategy_code:
                    logger.warning(f"⚠️ 未设置目标策略: {config['id']}")
                    continue
                
                # 执行反手策略
                logger.info(f"🔄 多单止损，反手开空: {account_id} -> {strategy_code}")
                
                stop_loss_info = {
                    'positions_closed': len(closed_positions),
                    'total_loss': sum([float(p.get('upl', 0)) for p in closed_positions]),
                    'warning_type': stop_loss_record.get('warning_type', '暴跌预警')
                }
                
                result = execute_reverse_strategy(
                    account_id, 
                    config['type'], 
                    strategy_code, 
                    closed_positions
                )
                
                # 更新触发权限（防止重复触发）
                update_trigger_permission(account_id, config['id'], allow_trigger=False)
                
                # 记录触发事件
                log_trigger_event(
                    account_id, 
                    config['id'], 
                    config['type'], 
                    strategy_code, 
                    result,
                    stop_loss_info
                )
                
                # 发送通知
                send_reverse_notification(
                    account_id,
                    config['type'],
                    strategy_code,
                    result,
                    stop_loss_info
                )
                
                # 标记止损记录为已处理
                mark_stop_loss_as_processed(account_id, stop_loss_record)
                
                break  # 找到并处理了配置，跳出循环


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🔄 止损反手开单监控器启动")
    logger.info(f"📋 监控账户: {', '.join(ACCOUNTS)}")
    logger.info(f"⏱️  检查间隔: {CHECK_INTERVAL} 秒")
    logger.info("=" * 60)
    
    while True:
        try:
            logger.info(f"🔍 开始检查止损反手触发条件...")
            
            for account_id in ACCOUNTS:
                try:
                    check_account(account_id)
                except Exception as e:
                    logger.error(f"❌ 检查账户失败 {account_id}: {e}", exc_info=True)
            
            logger.info(f"✅ 检查完成，等待 {CHECK_INTERVAL} 秒后继续...")
            time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("⏹️  收到停止信号，监控器退出")
            break
        except Exception as e:
            logger.error(f"❌ 监控器错误: {e}", exc_info=True)
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
