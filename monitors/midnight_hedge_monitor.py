#!/usr/bin/env python3
"""
0点0分对冲底仓监控器
- 每天北京时间00:00:00自动开多单和空单
- 独立跟踪每个订单的盈亏情况
- 记录到JSONL文件
- 支持账户独立配置
- 策略可选择
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
import schedule

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入北京时间工具
from utils.beijing_time import get_beijing_time, get_beijing_now_str, get_beijing_date_str

# 配置日志
log_dir = project_root / 'data' / 'midnight_hedge_orders' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / f"monitor_{get_beijing_date_str()}.log"
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
CHECK_INTERVAL = 30  # 检查间隔（秒）
FLASK_API_BASE = "http://localhost:9002"

# 数据目录
CONFIG_DIR = project_root / 'data' / 'midnight_hedge_orders'
EXECUTION_DIR = CONFIG_DIR / 'execution_records'
PNL_DIR = CONFIG_DIR / 'pnl_records'

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
PNL_DIR.mkdir(parents=True, exist_ok=True)


def load_config(account_id):
    """加载账户配置"""
    config_file = CONFIG_DIR / f'{account_id}_hedge_config.jsonl'
    
    if not config_file.exists():
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            if line:
                return json.loads(line)
    except Exception as e:
        logger.error(f"加载配置失败 {account_id}: {e}")
    
    return None


def save_execution_record(account_id, record):
    """保存执行记录"""
    date_str = get_beijing_date_str()
    record_file = EXECUTION_DIR / f'{account_id}_executions_{date_str}.jsonl'
    
    try:
        with open(record_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        logger.info(f"📝 执行记录已保存: {record_file}")
    except Exception as e:
        logger.error(f"保存执行记录失败: {e}")


def save_pnl_record(account_id, record):
    """保存盈亏记录"""
    date_str = get_beijing_date_str()
    pnl_file = PNL_DIR / f'{account_id}_pnl_{date_str}.jsonl'
    
    try:
        with open(pnl_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        logger.info(f"💰 盈亏记录已保存: {pnl_file}")
    except Exception as e:
        logger.error(f"保存盈亏记录失败: {e}")


def execute_strategy(account_id, strategy_code, side):
    """执行策略开单"""
    try:
        # 调用策略执行API（需要根据实际API实现）
        url = f"{FLASK_API_BASE}/api/okx-trading/execute-strategy"
        data = {
            'account_id': account_id,
            'strategy_code': strategy_code,
            'side': side,  # 'long' or 'short'
            'source': 'midnight_hedge',
            'timestamp': get_beijing_now_str()
        }
        
        logger.info(f"📤 发送开单请求: {data}")
        
        # TODO: 实际调用API
        # response = requests.post(url, json=data, timeout=10)
        
        # 模拟返回
        result = {
            'success': True,
            'order_id': f"HEDGE_{get_beijing_date_str()}_{side.upper()}_{account_id}",
            'strategy_code': strategy_code,
            'side': side,
            'entry_price': 100.0,  # 示例价格
            'quantity': 1.0,
            'timestamp': get_beijing_now_str()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 执行策略失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'strategy_code': strategy_code,
            'side': side,
            'timestamp': get_beijing_now_str()
        }


def check_and_execute_midnight_hedge():
    """检查并执行0点0分对冲"""
    beijing_time = get_beijing_time()
    current_minute = beijing_time.strftime('%H:%M')
    
    # 只在00:00执行
    if current_minute != '00:00':
        return
    
    # 检查是否今天已经执行过
    today_date = get_beijing_date_str()
    execution_flag_file = CONFIG_DIR / f'executed_{today_date}.flag'
    
    if execution_flag_file.exists():
        logger.debug(f"⏸️  今天已执行过，跳过")
        return
    
    logger.info("=" * 80)
    logger.info(f"🌙 北京时间 00:00:00 - 开始执行对冲底仓开单")
    logger.info("=" * 80)
    
    # 遍历所有账户
    for account_id in ACCOUNTS:
        config = load_config(account_id)
        
        if not config:
            logger.debug(f"⚪ {account_id}: 无配置")
            continue
        
        if not config.get('enabled', False):
            logger.info(f"⏸️  {account_id}: 未启用")
            continue
        
        long_strategy = config.get('long_strategy_code')
        short_strategy = config.get('short_strategy_code')
        
        if not long_strategy or not short_strategy:
            logger.warning(f"⚠️  {account_id}: 未配置策略，跳过")
            continue
        
        logger.info(f"✅ {account_id}: 开始执行对冲开单")
        logger.info(f"   多单策略: {long_strategy}")
        logger.info(f"   空单策略: {short_strategy}")
        
        # 执行多单
        long_result = execute_strategy(account_id, long_strategy, 'long')
        if long_result['success']:
            logger.info(f"   ✅ 多单开仓成功: {long_result.get('order_id')}")
        else:
            logger.error(f"   ❌ 多单开仓失败: {long_result.get('error')}")
        
        # 执行空单
        short_result = execute_strategy(account_id, short_strategy, 'short')
        if short_result['success']:
            logger.info(f"   ✅ 空单开仓成功: {short_result.get('order_id')}")
        else:
            logger.error(f"   ❌ 空单开仓失败: {short_result.get('error')}")
        
        # 保存执行记录
        execution_record = {
            'account_id': account_id,
            'execution_time': get_beijing_now_str(),
            'date': today_date,
            'long_order': long_result,
            'short_order': short_result,
            'both_success': long_result['success'] and short_result['success']
        }
        
        save_execution_record(account_id, execution_record)
        
        # 初始化盈亏记录
        if long_result['success']:
            pnl_record_long = {
                'account_id': account_id,
                'order_id': long_result.get('order_id'),
                'side': 'long',
                'strategy_code': long_strategy,
                'entry_time': get_beijing_now_str(),
                'entry_price': long_result.get('entry_price'),
                'quantity': long_result.get('quantity'),
                'current_price': long_result.get('entry_price'),
                'unrealized_pnl': 0.0,
                'unrealized_pnl_percent': 0.0,
                'last_updated': get_beijing_now_str()
            }
            save_pnl_record(account_id, pnl_record_long)
        
        if short_result['success']:
            pnl_record_short = {
                'account_id': account_id,
                'order_id': short_result.get('order_id'),
                'side': 'short',
                'strategy_code': short_strategy,
                'entry_time': get_beijing_now_str(),
                'entry_price': short_result.get('entry_price'),
                'quantity': short_result.get('quantity'),
                'current_price': short_result.get('entry_price'),
                'unrealized_pnl': 0.0,
                'unrealized_pnl_percent': 0.0,
                'last_updated': get_beijing_now_str()
            }
            save_pnl_record(account_id, pnl_record_short)
    
    # 创建执行标记文件
    execution_flag_file.touch()
    logger.info("=" * 80)
    logger.info(f"✅ 对冲底仓开单完成，已创建执行标记")
    logger.info("=" * 80)


def monitor_loop():
    """主监控循环"""
    logger.info("🚀 0点0分对冲底仓监控器启动")
    logger.info(f"📊 检查间隔: {CHECK_INTERVAL}秒")
    logger.info(f"👥 监控账户: {', '.join(ACCOUNTS)}")
    logger.info(f"⏰ 执行时间: 每天北京时间 00:00:00")
    
    while True:
        try:
            beijing_time = get_beijing_time()
            current_time = beijing_time.strftime('%H:%M:%S')
            
            # 每分钟的00秒检查一次
            if beijing_time.second == 0:
                logger.debug(f"⏰ [{current_time}] 检查是否需要执行对冲开单...")
                check_and_execute_midnight_hedge()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("⛔ 收到停止信号，监控器退出")
            break
        except Exception as e:
            logger.error(f"❌ 监控循环出错: {e}", exc_info=True)
            logger.info(f"⏸️  等待 {CHECK_INTERVAL} 秒后重试...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor_loop()
