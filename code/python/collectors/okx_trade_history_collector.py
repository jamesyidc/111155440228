#!/usr/bin/env python3
"""
OKX交易历史数据采集器
定期获取OKX交易记录并保存为JSONL格式
"""

import os
import sys
import json
import time
import hmac
import base64
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'okx_trading_history'

# 主账户API配置
MAIN_ACCOUNT = {
    'api_key': 'b0c18f2d-e014-4ae8-9c3c-cb02161de4db',
    'api_secret': '92F864C599B2CE2EC5186AD14C8B4110',
    'passphrase': 'Tencent@123'
}

class OKXTradeCollector:
    def __init__(self):
        self.base_url = 'https://www.okx.com'
        self.api_key = MAIN_ACCOUNT['api_key']
        self.api_secret = MAIN_ACCOUNT['api_secret']
        self.passphrase = MAIN_ACCOUNT['passphrase']
        
    def _generate_signature(self, timestamp, method, request_path):
        """生成签名"""
        message = timestamp + method + request_path
        mac = hmac.new(
            bytes(self.api_secret, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod='sha256'
        )
        return base64.b64encode(mac.digest()).decode()
    
    def _get_headers(self, method, request_path):
        """生成请求头"""
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        signature = self._generate_signature(timestamp, method, request_path)
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def fetch_trades(self, start_ts, end_ts, limit=100):
        """获取交易历史"""
        request_path = f'/api/v5/trade/fills-history?instType=SWAP&begin={start_ts}&end={end_ts}&limit={limit}'
        headers = self._get_headers('GET', request_path)
        
        try:
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=10
            )
            result = response.json()
            
            if result.get('code') == '0':
                return result.get('data', [])
            else:
                print(f"❌ API错误: {result.get('msg', '未知错误')}")
                return []
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return []
    
    def fetch_all_trades(self, days=7):
        """获取指定天数的所有交易"""
        now = datetime.now()
        start_time = now - timedelta(days=days)
        
        start_ts = int(start_time.timestamp() * 1000)
        end_ts = int(now.timestamp() * 1000)
        
        print(f"📊 获取交易历史: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ~ {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_trades = []
        batch = 1
        
        while True:
            print(f"  批次 {batch}: ", end='', flush=True)
            trades = self.fetch_trades(start_ts, end_ts, limit=100)
            
            if not trades:
                print("无数据")
                break
            
            print(f"获取 {len(trades)} 笔")
            all_trades.extend(trades)
            
            # 获取最后一笔的时间戳，用于下一次请求
            last_ts = int(trades[-1].get('ts', 0))
            if last_ts <= start_ts:
                break
            
            end_ts = last_ts - 1
            batch += 1
            time.sleep(0.2)  # 避免频率限制
            
            # 限制最多获取1000笔
            if len(all_trades) >= 1000:
                break
        
        print(f"✅ 总共获取 {len(all_trades)} 笔交易")
        return all_trades
    
    def save_trades(self, trades):
        """保存交易记录到JSONL"""
        if not trades:
            print("⚠️ 无交易数据需要保存")
            return
        
        # 按日期分组
        trades_by_date = {}
        for trade in trades:
            ts = int(trade.get('ts', 0))
            if ts == 0:
                continue
            
            trade_time = datetime.fromtimestamp(ts / 1000)
            date_str = trade_time.strftime('%Y%m%d')
            
            if date_str not in trades_by_date:
                trades_by_date[date_str] = []
            
            # 转换为标准格式
            trade_data = {
                'instId': trade.get('instId', ''),
                'side': trade.get('side', ''),
                'posSide': trade.get('posSide', ''),
                'px': float(trade.get('px', 0)),
                'sz': float(trade.get('sz', 0)),
                'fillTime': ts,
                'fillPx': float(trade.get('fillPx', 0)),
                'fillSz': float(trade.get('fillSz', 0)),
                'fee': float(trade.get('fee', 0)),
                'tradeId': trade.get('tradeId', ''),
                'ordId': trade.get('ordId', ''),
                'clOrdId': trade.get('clOrdId', ''),
                'tag': trade.get('tag', ''),
                'fillTime_str': trade_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            trades_by_date[date_str].append(trade_data)
        
        # 保存到文件
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        for date_str, date_trades in trades_by_date.items():
            file_path = DATA_DIR / f'okx_trades_{date_str}.jsonl'
            
            # 读取已有数据
            existing_ids = set()
            if file_path.exists():
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            existing_ids.add(data.get('tradeId'))
            
            # 只保存新数据
            new_trades = [t for t in date_trades if t['tradeId'] not in existing_ids]
            
            if new_trades:
                with open(file_path, 'a') as f:
                    for trade in new_trades:
                        f.write(json.dumps(trade, ensure_ascii=False) + '\n')
                
                print(f"  📝 {date_str}: 新增 {len(new_trades)} 笔 (文件: {file_path.name})")
            else:
                print(f"  ✓ {date_str}: 无新数据")
    
    def run(self, days=7):
        """运行采集"""
        print("🚀 OKX交易历史采集器启动")
        print(f"⏰ 采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 采集范围: 最近 {days} 天")
        print()
        
        # 获取交易数据
        trades = self.fetch_all_trades(days)
        
        # 保存数据
        if trades:
            print()
            print("💾 保存数据...")
            self.save_trades(trades)
            print()
            print("✅ 采集完成")
        else:
            print()
            print("⚠️ 未获取到交易数据")

def main():
    """主函数"""
    collector = OKXTradeCollector()
    
    # 默认采集最近7天
    days = 7
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print("❌ 参数错误，使用默认值: 7天")
    
    collector.run(days)

if __name__ == '__main__':
    main()
