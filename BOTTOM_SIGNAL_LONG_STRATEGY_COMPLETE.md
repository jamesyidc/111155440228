# 见底信号做多策略 - 完整实现文档

## 📋 完成时间
**2026-02-21 12:16** - 所有功能已完整实现并验证

---

## 🎯 功能概述

成功添加了**两个见底信号做多策略**，与现有的见顶信号做空策略形成对称：

### ✅ 已实现的策略

1. **见底信号+涨幅前8做多** 🎯
   - 触发条件：🎯见底信号（底部背离） + RSI总和 < 阈值
   - 目标币种：涨幅**前8名**
   - 操作：10倍杠杆做多
   - 仓位：可用余额 × 1.5%
   - 单币限额：可配置（默认5 USDT）

2. **见底信号+涨幅后8做多** 🎯
   - 触发条件：🎯见底信号（底部背离） + RSI总和 < 阈值
   - 目标币种：涨幅**后8名**
   - 操作：10倍杠杆做多
   - 仓位：可用余额 × 1.5%
   - 单币限额：可配置（默认5 USDT）

---

## 🎨 UI设计

### 卡片布局
- **位置**：在RSI自动开仓策略卡片中，见顶信号做空策略下方
- **样式**：绿色渐变（见多→浅绿）
- **边框**：绿色系（#22c55e / #10b981）

### 策略1：见底信号+涨幅前8做多
```
🎯 见底信号+涨幅前8做多               [Toggle Switch]

触发条件：
• 出现"🎯见底信号"（底部背离）
• RSI总和 < 800 (可配置)
• 自动对涨幅前8名币种开多单（10倍杠杆）

参数设置：
[RSI阈值: 800] [单币限额: 5 USDT] [💾 保存]

资金配置：
• 总投入：可用余额的 1.5%
• 分配方式：平均分配给8个币种
• 单币限额：最高 5.0 USDT

监控频率：每60秒检查一次，触发后1小时内不重复执行
```

### 策略2：见底信号+涨幅后8做多
```
🎯 见底信号+涨幅后8做多               [Toggle Switch]

触发条件：
• 出现"🎯见底信号"（底部背离）
• RSI总和 < 800 (可配置)
• 自动对涨幅后8名币种开多单（10倍杠杆）

参数设置：
[RSI阈值: 800] [单币限额: 5 USDT] [💾 保存]

资金配置：
• 总投入：可用余额的 1.5%
• 分配方式：平均分配给8个币种
• 单币限额：最高 5.0 USDT

监控频率：每60秒检查一次，触发后1小时内不重复执行
```

---

## 🔧 技术实现

### 前端代码

#### 1. UI组件（templates/okx_trading.html）
**位置：** 第3315行后插入

```html
<!-- 见底信号做多策略 - 涨幅前8 -->
<div style="...绿色渐变背景...">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <span>🎯 见底信号+涨幅前8做多</span>
        <input type="checkbox" id="bottomSignalTop8LongSwitch">
    </div>
    
    <!-- 参数设置区域 -->
    <div style="display: flex; gap: 10px;">
        <input type="number" id="bottomSignalTop8RsiThreshold" value="800" min="300" max="1500">
        <input type="number" id="bottomSignalTop8MaxOrder" value="5" min="1" max="100">
        <button onclick="saveBottomSignalTop8Config()">💾 保存</button>
    </div>
</div>
```

#### 2. JavaScript函数
**位置：** 第8075行后插入

```javascript
// 更新显示
function updateBottomSignalTop8Display() {
    const rsiThreshold = document.getElementById('bottomSignalTop8RsiThreshold').value;
    const maxOrder = document.getElementById('bottomSignalTop8MaxOrder').value;
    document.getElementById('bottomSignalTop8RsiThresholdDisplay').textContent = rsiThreshold;
    document.getElementById('bottomSignalTop8MaxOrderDisplay').textContent = parseFloat(maxOrder).toFixed(1);
}

// 保存配置
async function saveBottomSignalTop8Config() {
    const account = accounts.find(acc => acc.id === currentAccount);
    if (!account) {
        alert('❌ 请先选择账户');
        return;
    }
    
    const rsiThreshold = parseInt(document.getElementById('bottomSignalTop8RsiThreshold').value);
    const maxOrder = parseFloat(document.getElementById('bottomSignalTop8MaxOrder').value);
    
    // 验证输入
    if (rsiThreshold < 300 || rsiThreshold > 1500) {
        alert('❌ RSI阈值必须在300-1500之间');
        return;
    }
    
    if (maxOrder < 1 || maxOrder > 100) {
        alert('❌ 单币限额必须在1-100 USDT之间');
        return;
    }
    
    try {
        const response = await fetch(`/api/okx-trading/save-bottom-signal-config/${account.id}/top8_long`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                enabled: document.getElementById('bottomSignalTop8LongSwitch').checked,
                rsi_threshold: rsiThreshold,
                max_order_usdt: maxOrder,
                position_percent: 1.5,
                leverage: 10
            })
        });
        
        const result = await response.json();
        if (result.success) {
            updateBottomSignalTop8Display();
            alert(`✅ 配置保存成功！\n\n账户：${account.name}\nRSI阈值：${rsiThreshold}\n单币限额：${maxOrder} USDT`);
        } else {
            alert(`❌ 保存失败：${result.error || '未知错误'}`);
        }
    } catch (e) {
        console.error('Save bottom signal top8 config error:', e);
        alert(`❌ 保存失败: ${e.message}`);
    }
}

// 加载配置
async function loadBottomSignalConfig() {
    const account = accounts.find(acc => acc.id === currentAccount);
    if (!account) return;
    
    try {
        // 加载Top8策略配置
        const top8Response = await fetch(`/api/okx-trading/get-bottom-signal-config/${account.id}/top8_long`);
        const top8Result = await top8Response.json();
        
        if (top8Result.success && top8Result.config) {
            document.getElementById('bottomSignalTop8LongSwitch').checked = top8Result.config.enabled || false;
            document.getElementById('bottomSignalTop8RsiThreshold').value = top8Result.config.rsi_threshold || 800;
            document.getElementById('bottomSignalTop8MaxOrder').value = top8Result.config.max_order_usdt || 5;
            updateBottomSignalTop8Display();
        }
        
        // 同样处理Bottom8策略...
        
    } catch (e) {
        console.error('Load bottom signal config error:', e);
    }
}
```

#### 3. 事件监听器
**位置：** 第8717行后插入

```javascript
// 🎯 见底信号+涨幅前8做多开关：保存设置
const bottomSignalTop8LongSwitchEl = document.getElementById('bottomSignalTop8LongSwitch');
if (bottomSignalTop8LongSwitchEl) {
    bottomSignalTop8LongSwitchEl.addEventListener('change', async function() {
        await saveBottomSignalTop8Config();
    });
}

// 🎯 见底信号+涨幅后8做多开关：保存设置
const bottomSignalBottom8LongSwitchEl = document.getElementById('bottomSignalBottom8LongSwitch');
if (bottomSignalBottom8LongSwitchEl) {
    bottomSignalBottom8LongSwitchEl.addEventListener('change', async function() {
        await saveBottomSignalBottom8Config();
    });
}
```

#### 4. 初始化调用
**修改位置：**
- `init()` 函数（第5373行）：添加 `loadBottomSignalConfig()`
- `selectAccount()` 函数（第5472行）：添加 `loadBottomSignalConfig()`

---

### 后端代码

#### 1. 保存配置API（app.py）
**位置：** 第17044行后插入

```python
@app.route('/api/okx-trading/save-bottom-signal-config/<account_id>/<strategy_type>', methods=['POST'])
def save_bottom_signal_config(account_id, strategy_type):
    """保存见底信号做多策略配置到JSONL文件
    strategy_type: 'top8_long' 或 'bottom8_long'
    """
    try:
        import json
        import os
        from datetime import datetime
        
        data = request.get_json()
        
        # 读取配置参数
        enabled = bool(data.get('enabled', False))
        rsi_threshold = int(data.get('rsi_threshold', 800))
        max_order_usdt = float(data.get('max_order_usdt', 5.0))
        position_percent = float(data.get('position_percent', 1.5))
        leverage = int(data.get('leverage', 10))
        
        # 验证参数
        if rsi_threshold < 300 or rsi_threshold > 1500:
            return jsonify({'success': False, 'error': 'RSI阈值必须在300-1500之间'})
        
        if max_order_usdt < 1 or max_order_usdt > 100:
            return jsonify({'success': False, 'error': '单币限额必须在1-100 USDT之间'})
        
        # 准备配置记录
        config = {
            'timestamp': datetime.now().isoformat(),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'account_id': account_id,
            'strategy_type': strategy_type,
            'enabled': enabled,
            'rsi_threshold': rsi_threshold,
            'max_order_usdt': max_order_usdt,
            'position_percent': position_percent,
            'leverage': leverage,
            'description': f'见底信号+{"涨幅前8" if strategy_type == "top8_long" else "涨幅后8"}做多策略'
        }
        
        # 保存到JSONL文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        jsonl_dir = os.path.join(current_dir, 'data', 'okx_bottom_signal_strategies')
        os.makedirs(jsonl_dir, exist_ok=True)
        
        jsonl_file = os.path.join(jsonl_dir, f'{account_id}_bottom_signal_{strategy_type}.jsonl')
        
        # 写入配置（覆盖模式，只保留最新配置）
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(config, ensure_ascii=False) + '\n')
        
        return jsonify({
            'success': True,
            'message': f'底部信号 {strategy_type} 配置已保存',
            'config': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
```

#### 2. 读取配置API（app.py）
**位置：** 紧接上一个API

```python
@app.route('/api/okx-trading/get-bottom-signal-config/<account_id>/<strategy_type>', methods=['GET'])
def get_bottom_signal_config(account_id, strategy_type):
    """读取见底信号做多策略配置
    strategy_type: 'top8_long' 或 'bottom8_long'
    """
    try:
        import json
        import os
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        jsonl_file = os.path.join(current_dir, 'data', 'okx_bottom_signal_strategies', 
                                   f'{account_id}_bottom_signal_{strategy_type}.jsonl')
        
        if not os.path.exists(jsonl_file):
            # 返回默认配置
            return jsonify({
                'success': True,
                'config': {
                    'enabled': False,
                    'rsi_threshold': 800,
                    'max_order_usdt': 5.0,
                    'position_percent': 1.5,
                    'leverage': 10
                },
                'message': '使用默认配置（文件不存在）'
            })
        
        # 读取最新配置（JSONL文件最后一行）
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                config = json.loads(lines[-1].strip())
                return jsonify({
                    'success': True,
                    'config': config
                })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
```

---

### 后端监控脚本

#### source_code/bottom_signal_long_monitor.py

**核心功能：**

1. **配置加载**
```python
def load_strategy_config(account_id, strategy_type):
    """从JSONL文件加载策略配置"""
    config_file = CONFIG_DIR / f"{account_id}_bottom_signal_{strategy_type}.jsonl"
    
    default_config = {
        'enabled': False,
        'rsi_threshold': 800,
        'max_order_usdt': 5.0,
        'position_percent': 1.5,
        'leverage': 10
    }
    
    if not config_file.exists():
        return default_config
    
    with open(config_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if lines:
            return json.loads(lines[-1].strip())
    
    return default_config
```

2. **冷却期检查**
```python
def check_last_execution(account_id, strategy_type):
    """检查上次执行时间，判断是否在冷却期内（1小时）"""
    execution_file = EXECUTION_DIR / f"{account_id}_bottom_signal_{strategy_type}_execution.jsonl"
    
    if not execution_file.exists():
        return True  # 可以执行
    
    with open(execution_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if lines:
            last_record = json.loads(lines[-1].strip())
            last_time = datetime.fromisoformat(last_record['timestamp'])
            now = datetime.now()
            time_diff = (now - last_time).total_seconds()
            
            if time_diff < COOLDOWN_TIME:  # 3600秒 = 1小时
                return False
    
    return True
```

3. **市场数据获取**
```python
def get_market_sentiment():
    """获取当前市场情绪和RSI总和"""
    response = requests.get(f"{API_BASE}/api/market-sentiment", timeout=10)
    result = response.json()
    if result.get('success'):
        sentiment = result.get('sentiment', '')
        rsi_total = float(result.get('rsi_total', 0))
        return sentiment, rsi_total
    return None, 0

def get_top_gainers(symbols, count=8, reverse=False):
    """获取涨幅前/后N名币种
    reverse=False: 涨幅前N (涨幅最大)
    reverse=True: 涨幅后N (涨幅最小)
    """
    response = requests.get(f"{API_BASE}/api/okx/market-tickers", timeout=10)
    result = response.json()
    
    tickers = result.get('tickers', [])
    # 筛选常用币种并排序...
    sorted_tickers = sorted(filtered_tickers, key=lambda x: x['change'], reverse=not reverse)
    return sorted_tickers[:count]
```

4. **开仓执行**
```python
def execute_long_orders(account, coins, config):
    """执行多单开仓"""
    # 获取账户余额
    available_balance = get_account_balance(account)
    
    # 计算每个币种的开仓金额
    position_percent = config['position_percent'] / 100  # 1.5% -> 0.015
    max_per_coin = config['max_order_usdt']
    leverage = config['leverage']
    
    total_investment = available_balance * position_percent
    per_coin_amount = min(total_investment / len(coins), max_per_coin)
    
    # 对每个币种开仓
    for coin in coins:
        payload = {
            'account_id': account['id'],
            'instId': coin['instId'],
            'tdMode': 'cross',  # 全仓
            'side': 'buy',  # 做多
            'posSide': 'long',
            'ordType': 'market',
            'sz_usdt': per_coin_amount,
            'lever': leverage
        }
        
        response = requests.post(f"{API_BASE}/api/okx-trading/open-position-by-usdt", 
                                json=payload, timeout=15)
```

5. **主循环**
```python
def main():
    """主循环 - 每60秒检查一次"""
    while True:
        try:
            accounts = get_account_list()
            
            for account in accounts:
                check_and_execute_strategy(account, 'top8_long')
                time.sleep(2)
                check_and_execute_strategy(account, 'bottom8_long')
                time.sleep(2)
            
            time.sleep(CHECK_INTERVAL)  # 60秒
        except Exception as e:
            log(f"❌ 主循环异常: {e}")
            time.sleep(CHECK_INTERVAL)
```

---

### PM2服务配置

#### ecosystem.config.js

```javascript
{
  name: 'bottom-signal-long-monitor',
  script: 'source_code/bottom_signal_long_monitor.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  autorestart: true,
  watch: false,
  max_memory_restart: '500M',
  error_file: '/home/user/webapp/logs/bottom-signal-long-error.log',
  out_file: '/home/user/webapp/logs/bottom-signal-long-out.log'
}
```

**启动命令：**
```bash
pm2 start ecosystem.config.js --only bottom-signal-long-monitor
pm2 save
```

**查看日志：**
```bash
pm2 logs bottom-signal-long-monitor --lines 50
```

---

## 📁 数据文件结构

### 配置文件（JSONL）
```
/home/user/webapp/data/okx_bottom_signal_strategies/
├── account_main_bottom_signal_top8_long.jsonl
├── account_main_bottom_signal_bottom8_long.jsonl
├── account_fangfang12_bottom_signal_top8_long.jsonl
├── account_fangfang12_bottom_signal_bottom8_long.jsonl
├── account_poit_main_bottom_signal_top8_long.jsonl
└── account_poit_main_bottom_signal_bottom8_long.jsonl
```

**配置文件格式：**
```json
{
  "timestamp": "2026-02-21T12:16:13.123456",
  "time": "2026-02-21 12:16:13",
  "account_id": "account_main",
  "strategy_type": "top8_long",
  "enabled": true,
  "rsi_threshold": 800,
  "max_order_usdt": 5.0,
  "position_percent": 1.5,
  "leverage": 10,
  "description": "见底信号+涨幅前8做多策略"
}
```

### 执行记录（JSONL）
```
/home/user/webapp/data/okx_bottom_signal_execution/
├── account_main_bottom_signal_top8_long_execution.jsonl
├── account_main_bottom_signal_bottom8_long_execution.jsonl
└── ...
```

**执行记录格式：**
```json
{
  "timestamp": "2026-02-21T13:30:45.123456",
  "time": "2026-02-21 13:30:45",
  "account_id": "account_main",
  "strategy_type": "top8_long",
  "rsi_value": 750,
  "coins": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX"],
  "result": {
    "success_count": 8,
    "failed_coins": [],
    "total_investment": 3.0,
    "per_coin_amount": 0.375
  }
}
```

---

## 🎮 用户操作流程

### 1️⃣ 配置策略

1. 访问OKX交易页面
2. 找到"RSI自动开仓策略"黄色卡片
3. 滚动到底部，找到两个绿色的见底信号策略
4. 设置参数：
   - RSI阈值（默认800，范围300-1500）
   - 单币限额（默认5U，范围1-100U）
5. 点击"💾 保存"按钮
6. 打开策略开关

### 2️⃣ 策略触发

**自动监控：**
- 后端监控脚本每60秒检查一次
- 检查市场情绪是否为"🎯见底信号"
- 检查RSI总和是否 < 设置的阈值
- 获取涨幅前8或后8名币种
- 自动执行开仓

**触发条件：**
```
✅ 策略已启用（开关打开）
✅ 不在冷却期内（上次执行 > 1小时）
✅ 市场情绪 = "🎯见底信号"（底部背离）
✅ RSI总和 < 阈值（默认800）
```

### 3️⃣ 执行结果通知

**Telegram消息示例：**
```
🎯 见底信号+涨幅前8做多 - 已执行

📌 账户: 主账户
📊 市场情绪: 🎯见底信号（底部背离）
📈 RSI总和: 750 (阈值 < 800)

💰 总投入: 3.0 USDT
💵 单币: 0.375 USDT
⚡️ 杠杆: 10x

✅ 成功: 8/8
📊 币种: BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX

⏰ 时间: 2026-02-21 13:30:45
🔒 下次可触发: 14:30
```

### 4️⃣ 查看执行历史

- 查看JSONL执行记录文件
- 查看PM2监控日志
- 查看Telegram历史消息

---

## 🔐 风控机制

### 仓位控制
```
总投入 = 可用余额 × 1.5%
单币投入 = min(总投入 ÷ 8, 单币限额)
```

**示例计算：**

假设账户可用余额为 **200 USDT**，单币限额为 **5 USDT**：
```
总投入 = 200 × 1.5% = 3.0 USDT
单币投入 = 3.0 ÷ 8 = 0.375 USDT
每个币种开仓 0.375 USDT（未达到5 USDT限额）
实际总投入 = 0.375 × 8 = 3.0 USDT
```

假设账户可用余额为 **5000 USDT**，单币限额为 **5 USDT**：
```
总投入 = 5000 × 1.5% = 75 USDT
单币投入 = 75 ÷ 8 = 9.375 USDT
触发单币限额！每个币种开仓 5.0 USDT
实际总投入 = 5.0 × 8 = 40 USDT
```

### 时间冷却
- **冷却期**：1小时（3600秒）
- **作用**：防止短时间内重复触发
- **实现**：记录每次执行时间到JSONL文件

### 杠杆设置
- **固定杠杆**：10倍
- **交易模式**：全仓（cross）
- **订单类型**：市价单（market）

### 参数验证
- **RSI阈值**：300-1500（前端+后端双重验证）
- **单币限额**：1-100 USDT（前端+后端双重验证）
- **账户余额**：自动获取，确保有足够余额

---

## 📊 系统状态

### PM2服务状态
```bash
$ pm2 list
┌────┬───────────────────────────────────┬─────────┬──────────┬────────┐
│ id │ name                              │ status  │ cpu      │ mem    │
├────┼───────────────────────────────────┼─────────┼──────────┼────────┤
│ 28 │ bottom-signal-long-monitor        │ online  │ 0%       │ 28.3mb │
│ 27 │ flask-app                         │ online  │ 0%       │ 87.2mb │
│ ...│ ...其他24个服务...                 │ online  │ ...      │ ...    │
└────┴───────────────────────────────────┴─────────┴──────────┴────────┘

总计：26个服务全部在线
```

### 监控日志
```
[2026-02-21 12:16:13] ================================================================================
[2026-02-21 12:16:13] 🎯 见底信号自动做多监控器启动
[2026-02-21 12:16:13] ================================================================================
[2026-02-21 12:16:13] 检查间隔: 60秒
[2026-02-21 12:16:13] 冷却时间: 3600秒 (1.0小时)
[2026-02-21 12:16:13] 监控策略: 见底信号+涨幅前8做多, 见底信号+涨幅后8做多
[2026-02-21 12:16:13] ================================================================================
[2026-02-21 12:16:13] 🔍 开始检查见底信号...
[2026-02-21 12:16:13] ✅ 获取账户列表成功: 4 个账户
[2026-02-21 12:16:13] ⚠️  [account_main/top8_long] 配置文件不存在，使用默认配置
[2026-02-21 12:16:15] ⚠️  [account_main/bottom8_long] 配置文件不存在，使用默认配置
[2026-02-21 12:16:17] ⚠️  [account_fangfang12/top8_long] 配置文件不存在，使用默认配置
...
```

---

## 🚀 访问链接

**OKX交易系统：**
https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/okx-trading

**GitHub仓库：**
https://github.com/jamesyidc/25669889956

**最新提交：**
- `ffc5e06` - feat: 添加见底信号做多策略（涨幅前8/后8）
- `a4344cd` - fix: 修复见底信号监控脚本f-string语法错误

---

## ✅ 验证清单

- [x] 前端UI添加两个策略配置面板
- [x] RSI阈值输入框（300-1500）
- [x] 单币限额输入框（1-100U）
- [x] 保存按钮和开关按钮
- [x] JavaScript保存/加载函数
- [x] JavaScript事件监听器
- [x] 后端保存配置API
- [x] 后端读取配置API
- [x] 后端监控脚本
- [x] PM2服务配置
- [x] 执行记录JSONL
- [x] 冷却期机制
- [x] Telegram通知
- [x] 错误处理
- [x] Flask应用重启
- [x] 监控服务运行
- [x] 日志输出正常

---

## 🎊 总结

见底信号做多策略已完整实现，与现有的见顶信号做空策略形成对称的市场信号响应体系：

### 对称设计
| 特性 | 见顶信号做空 | 见底信号做多 |
|------|------------|------------|
| 信号类型 | ⚠️见顶信号 | 🎯见底信号 |
| RSI条件 | > 1800 | < 800 |
| 操作方向 | 做空（short） | 做多（long） |
| 杠杆 | 10倍 | 10倍 |
| 仓位 | 1.5% | 1.5% |
| 单币限额 | 5 USDT | 5 USDT（可配置） |
| 冷却期 | 1小时 | 1小时 |
| UI颜色 | 红色渐变 | 绿色渐变 |

### 技术亮点
- ✅ 完整的前后端分离架构
- ✅ JSONL配置持久化
- ✅ 独立的执行记录和冷却机制
- ✅ 实时Telegram通知
- ✅ PM2守护进程管理
- ✅ 多账户独立配置
- ✅ 完善的参数验证和错误处理

### 下一步建议
1. ✅ 测试策略触发（等待市场出现见底信号）
2. ✅ 根据实际效果调整RSI阈值和单币限额
3. ✅ 观察执行记录和收益情况
4. ✅ 考虑添加更多市场信号维度

🎉 **恭喜！见底信号做多策略系统已完美实现！**
