#!/usr/bin/env python3
"""
止损反手开单监控器
- 监控所有账户的止损事件
- 当检测到止损时，根据配置自动反向开仓
- 防重复触发机制
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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

# 确保目录存在
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
TRIGGER_EVENTS_DIR.mkdir(parents=True, exist_ok=True)


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


def log_trigger_event(account_id, config_id, config_type, strategy_code, result):
    """记录触发事件"""
    event_file = TRIGGER_EVENTS_DIR / f"{account_id}_trigger_events_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    event = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'account_id': account_id,
        'config_id': config_id,
        'config_type': config_type,
        'strategy_code': strategy_code,
        'result': result,
        'success': result.get('success', False) if isinstance(result, dict) else False
    }
    
    try:
        with open(event_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
        logger.info(f"📝 触发事件已记录: {account_id}/{config_id}")
    except Exception as e:
        logger.error(f"❌ 记录触发事件失败: {e}")


def check_stoploss_events(account_id):
    """
    检查账户的止损事件
    
    这里需要实际实现检查止损的逻辑。
    可以通过以下方式：
    1. 查询OKX API获取最近的止损订单
    2. 读取本地止损日志文件
    3. 监听止损通知
    
    返回: [{'type': 'long' | 'short', 'symbol': 'BTC-USDT-SWAP', 'time': '2026-03-02 14:30:00'}]
    """
    # TODO: 实现实际的止损事件检查逻辑
    # 这里返回空列表，表示没有检测到止损事件
    return []


def execute_reverse_strategy(account_id, config_type, strategy_code):
    """
    执行反手策略
    
    这里需要实际实现执行策略的逻辑。
    可以调用现有的策略执行函数或API。
    """
    logger.info(f"🚀 执行反手策略: {account_id} - {config_type} - {strategy_code}")
    
    # TODO: 实现实际的策略执行逻辑
    # 返回执行结果
    result = {
        'success': True,
        'message': f'模拟执行策略 {strategy_code}',
        'strategy_code': strategy_code,
        'account_id': account_id
    }
    
    return result


def check_account(account_id):
    """检查单个账户的止损反手触发"""
    logger.debug(f"🔍 检查账户: {account_id}")
    
    # 加载配置
    configs = load_reverse_configs(account_id)
    if not configs:
        logger.debug(f"账户 {account_id} 没有配置")
        return
    
    # 检查止损事件
    stoploss_events = check_stoploss_events(account_id)
    if not stoploss_events:
        logger.debug(f"账户 {account_id} 没有止损事件")
        return
    
    logger.info(f"⚠️ 检测到 {len(stoploss_events)} 个止损事件: {account_id}")
    
    # 处理每个止损事件
    for event in stoploss_events:
        event_type = event.get('type')  # 'long' or 'short'
        
        # 查找对应的反手配置
        for config in configs:
            # 多单止损反手开空
            if event_type == 'long' and config['type'] == 'long_stoploss_reverse':
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
                result = execute_reverse_strategy(account_id, config['type'], strategy_code)
                
                # 更新触发权限（防止重复触发）
                update_trigger_permission(account_id, config['id'], allow_trigger=False)
                
                # 记录触发事件
                log_trigger_event(account_id, config['id'], config['type'], strategy_code, result)
            
            # 空单止损反手开多
            elif event_type == 'short' and config['type'] == 'short_stoploss_reverse':
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
                logger.info(f"🔄 空单止损，反手开多: {account_id} -> {strategy_code}")
                result = execute_reverse_strategy(account_id, config['type'], strategy_code)
                
                # 更新触发权限（防止重复触发）
                update_trigger_permission(account_id, config['id'], allow_trigger=False)
                
                # 记录触发事件
                log_trigger_event(account_id, config['id'], config['type'], strategy_code, result)


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
