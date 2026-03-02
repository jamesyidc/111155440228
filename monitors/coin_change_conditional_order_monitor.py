#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
27币涨跌幅条件单监控器
监控27个主流币种的涨跌幅之和，当达到条件单触发条件时执行对应策略
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
log_dir = project_root / 'data' / 'coin_change_conditional_orders' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f'monitor_{datetime.now().strftime("%Y%m%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 配置
MONITOR_INTERVAL = 60  # 检查间隔（秒）
FLASK_API_BASE = "http://localhost:9002"
ACCOUNTS = ["account_main", "account_fangfang12", "account_anchor", "account_poit", "account_poit_main", "account_dadanini"]

# 策略执行函数映射
STRATEGY_EXECUTORS = {
    'STG_SHORT_TOP8': 'execute_short_top8_strategy',
    'STG_SHORT_BOTTOM8': 'execute_short_bottom8_strategy',
    'STG_LONG_TOP8': 'execute_long_top8_strategy',
    'STG_LONG_BOTTOM8': 'execute_long_bottom8_strategy',
}


def get_coin_change_data():
    """获取27币涨跌幅数据"""
    try:
        # 从第一个可用账户获取数据（数据对所有账户都一样）
        for account_id in ACCOUNTS:
            url = f"{FLASK_API_BASE}/api/okx-trading/coin-change-tpsl-overview/{account_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('currentData'):
                    total_change = data['currentData'].get('total_change', 0)
                    logger.info(f"✅ 获取27币涨跌幅数据成功: {total_change}% (账户: {account_id})")
                    return total_change
        
        logger.warning("⚠️  未能从任何账户获取27币涨跌幅数据")
        return None
        
    except Exception as e:
        logger.error(f"❌ 获取27币涨跌幅数据失败: {e}")
        return None


def get_conditional_orders(account_id):
    """获取指定账户的条件单列表"""
    try:
        url = f"{FLASK_API_BASE}/api/okx-trading/coin-change-conditional-orders/{account_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('orders', [])
        
        return []
        
    except Exception as e:
        logger.error(f"❌ 获取账户 {account_id} 条件单失败: {e}")
        return []


def check_trigger_condition(order, total_change):
    """检查条件单是否满足触发条件"""
    if not order.get('enabled'):
        return False, "条件单未启用"
    
    if not order.get('allow_trigger'):
        return False, "触发权限已禁用（已触发过）"
    
    trigger_condition = order.get('trigger_condition')
    trigger_value = order.get('trigger_value', 0)
    
    if trigger_condition == 'above':
        # 开空单：涨跌幅之和 >= 触发值
        if total_change >= trigger_value:
            return True, f"满足条件: {total_change}% >= {trigger_value}%"
        else:
            return False, f"不满足条件: {total_change}% < {trigger_value}%"
    
    elif trigger_condition == 'below':
        # 开多单：涨跌幅之和 <= 触发值
        if total_change <= trigger_value:
            return True, f"满足条件: {total_change}% <= {trigger_value}%"
        else:
            return False, f"不满足条件: {total_change}% > {trigger_value}%"
    
    return False, "未知的触发条件"


def execute_strategy(account_id, order, total_change):
    """执行策略（这里需要调用实际的策略执行逻辑）"""
    strategy_code = order.get('target_strategy_code')
    order_id = order.get('id')
    
    logger.info(f"🎯 准备执行策略: {strategy_code} (账户: {account_id}, 条件单: {order_id})")
    logger.info(f"📊 当前27币涨跌幅之和: {total_change}%")
    
    # TODO: 这里需要集成实际的策略执行逻辑
    # 目前只记录日志和更新触发状态
    
    # 记录触发事件
    log_trigger_event(account_id, order, total_change, success=True, message="策略执行成功（模拟）")
    
    # 更新条件单状态（禁止重复触发）
    update_order_trigger_status(account_id, order_id, triggered=True)
    
    return True


def log_trigger_event(account_id, order, total_change, success, message):
    """记录触发事件到JSONL"""
    events_dir = project_root / 'data' / 'coin_change_conditional_orders' / 'trigger_events'
    events_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y%m%d')
    events_file = events_dir / f'{account_id}_trigger_events_{date_str}.jsonl'
    
    event = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'account_id': account_id,
        'order_id': order.get('id'),
        'order_type': order.get('order_type'),
        'trigger_condition': order.get('trigger_condition'),
        'trigger_value': order.get('trigger_value'),
        'actual_value': total_change,
        'target_strategy_code': order.get('target_strategy_code'),
        'success': success,
        'message': message
    }
    
    with open(events_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    logger.info(f"📝 触发事件已记录: {events_file}")


def update_order_trigger_status(account_id, order_id, triggered):
    """更新条件单触发状态"""
    try:
        if triggered:
            # 触发后禁止重复触发
            url = f"{FLASK_API_BASE}/api/okx-trading/coin-change-conditional-orders/{account_id}/{order_id}/trigger"
            data = {
                'allow_trigger': False,
                'last_triggered_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            # 重置触发状态
            url = f"{FLASK_API_BASE}/api/okx-trading/coin-change-conditional-orders/{account_id}/{order_id}/reset-trigger"
            data = {}
        
        # 这个API需要在app.py中添加
        # 目前暂时通过直接修改JSONL文件实现
        update_jsonl_trigger_status(account_id, order_id, triggered)
        
    except Exception as e:
        logger.error(f"❌ 更新触发状态失败: {e}")


def update_jsonl_trigger_status(account_id, order_id, triggered):
    """直接更新JSONL文件中的触发状态"""
    jsonl_file = project_root / 'data' / 'coin_change_conditional_orders' / f'{account_id}_conditional_orders.jsonl'
    
    if not jsonl_file.exists():
        return
    
    # 读取所有订单
    orders = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                orders.append(json.loads(line))
    
    # 更新目标订单
    updated = False
    for order in orders:
        if order.get('id') == order_id:
            order['allow_trigger'] = not triggered
            if triggered:
                order['last_triggered_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                order['triggered_count'] = order.get('triggered_count', 0) + 1
            order['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = True
            break
    
    if updated:
        # 写回文件
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for order in orders:
                f.write(json.dumps(order, ensure_ascii=False) + '\n')
        
        logger.info(f"✅ 已更新条件单 {order_id} 的触发状态")


def monitor_loop():
    """主监控循环"""
    logger.info("🚀 27币涨跌幅条件单监控器启动")
    logger.info(f"📊 监控间隔: {MONITOR_INTERVAL}秒")
    logger.info(f"👥 监控账户: {', '.join(ACCOUNTS)}")
    
    while True:
        try:
            logger.info("=" * 80)
            logger.info(f"🔍 开始检查条件单触发 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            
            # 获取27币涨跌幅数据
            total_change = get_coin_change_data()
            
            if total_change is None:
                logger.warning("⚠️  无法获取27币涨跌幅数据，跳过本次检查")
                time.sleep(MONITOR_INTERVAL)
                continue
            
            # 检查每个账户的条件单
            for account_id in ACCOUNTS:
                orders = get_conditional_orders(account_id)
                
                if not orders:
                    logger.debug(f"📋 账户 {account_id} 没有条件单")
                    continue
                
                logger.info(f"📋 账户 {account_id} 有 {len(orders)} 个条件单")
                
                for order in orders:
                    order_id = order.get('id')
                    strategy_code = order.get('target_strategy_code')
                    
                    # 检查是否满足触发条件
                    should_trigger, reason = check_trigger_condition(order, total_change)
                    
                    if should_trigger:
                        logger.info(f"🎯 条件单 {order_id} 满足触发条件!")
                        logger.info(f"   策略: {strategy_code}")
                        logger.info(f"   原因: {reason}")
                        
                        # 执行策略
                        success = execute_strategy(account_id, order, total_change)
                        
                        if success:
                            logger.info(f"✅ 条件单 {order_id} 执行成功")
                        else:
                            logger.error(f"❌ 条件单 {order_id} 执行失败")
                    else:
                        logger.debug(f"⏸️  条件单 {order_id} 不满足触发条件: {reason}")
            
            logger.info(f"✅ 检查完成，等待 {MONITOR_INTERVAL} 秒后继续...")
            time.sleep(MONITOR_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("⛔ 收到停止信号，监控器退出")
            break
        except Exception as e:
            logger.error(f"❌ 监控循环出错: {e}", exc_info=True)
            logger.info(f"⏸️  等待 {MONITOR_INTERVAL} 秒后重试...")
            time.sleep(MONITOR_INTERVAL)


if __name__ == "__main__":
    monitor_loop()
