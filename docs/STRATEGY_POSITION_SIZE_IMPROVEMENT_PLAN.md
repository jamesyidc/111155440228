# 策略开仓金额计算改进方案

## 📋 问题描述

**当前问题**：策略筛选器中的百分比（1.5%, 3%, 5%, 8%）是按第一个账户的账户总额计算的，而不是按每个账户的剩余可开仓金额计算。

**用户需求**：需要按照每个账户的剩余可开仓金额分别计算开仓金额，而不是统一的一个值。

## 🔍 问题分析

### 当前实现
```javascript
// 当前：统一显示百分比阈值
触发条件: 等待再涨 1.5% 后开仓 | 杠杆: 10x
```

问题：
- ❌ 所有账户使用相同的百分比
- ❌ 没有考虑各账户的实际可用资金
- ❌ 没有显示建议的开仓金额

### 目标实现
```javascript
// 目标：为每个账户计算具体开仓金额
账户A: 可用 1000 USDT → 建议开仓 15 USDT (1.5%)
账户B: 可用 500 USDT → 建议开仓 7.5 USDT (1.5%)
账户C: 可用 2000 USDT → 建议开仓 30 USDT (1.5%)
```

## 🎯 解决方案

### 1. 数据结构设计

需要从OKX获取每个账户的资金信息：

```javascript
// 账户数据结构
{
    accountName: "POIT (子账户)",
    apiKey: "...",
    apiSecret: "...",
    passphrase: "...",
    balance: {
        totalEquity: 4200,      // 账户总权益
        availableBalance: 3500,  // 可用余额
        positionMargin: 700,     // 持仓保证金
        maxPosition: 4200        // 最大持仓限额
    }
}
```

### 2. API集成

#### 2.1 获取账户余额
**端点**：`/api/v5/account/balance`

**请求参数**：
```javascript
{
    ccy: "USDT"  // 查询USDT余额
}
```

**响应数据**：
```json
{
    "code": "0",
    "data": [{
        "totalEq": "4200.5",
        "availBal": "3500.2"
    }]
}
```

#### 2.2 计算可开仓金额

```javascript
function calculatePositionSize(availableBalance, percentage, leverage) {
    // 可开仓金额 = 可用余额 * 百分比
    const positionSize = availableBalance * (percentage / 100);
    
    // 实际需要的保证金 = 开仓金额 / 杠杆
    const requiredMargin = positionSize / leverage;
    
    return {
        positionSize: positionSize.toFixed(2),
        requiredMargin: requiredMargin.toFixed(2)
    };
}
```

### 3. 前端实现方案

#### 3.1 加载账户余额

在coin_change_tracker.html中添加：

```javascript
// 加载所有账户的余额信息
async function loadAccountsBalance() {
    const accounts = JSON.parse(localStorage.getItem('okx_accounts') || '[]');
    
    for (let account of accounts) {
        if (!account.apiKey || !account.apiSecret || !account.passphrase) {
            continue;
        }
        
        try {
            const response = await fetch('/api/okx-trading/account-balance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    apiKey: account.apiKey,
                    apiSecret: account.apiSecret,
                    passphrase: account.passphrase
                })
            });
            
            const result = await response.json();
            if (result.success) {
                account.balance = {
                    totalEquity: parseFloat(result.data.totalEq),
                    availableBalance: parseFloat(result.data.availBal)
                };
            }
        } catch (error) {
            console.error(`加载账户 ${account.name} 余额失败:`, error);
        }
    }
    
    // 保存更新后的账户数据
    window.accountsWithBalance = accounts;
    return accounts;
}
```

#### 3.2 修改策略显示函数

```javascript
function applyStrategy(range, threshold, leverage, direction) {
    console.log(`🎯 应用策略: ${range}, 阈值: ${threshold}%, 杠杆: ${leverage}x, 方向: ${direction}`);
    
    // 获取币种数据
    if (!window.currentCoinsData || window.currentCoinsData.length === 0) {
        alert('❌ 暂无数据，请等待数据加载完成！');
        return;
    }
    
    // 选择目标币种
    const sortedCoins = [...window.currentCoinsData].sort((a, b) => b.change - a.change);
    let targetCoins = range === 'top8' ? sortedCoins.slice(0, 8) : sortedCoins.slice(-8).reverse();
    
    // 获取账户余额信息
    const accounts = window.accountsWithBalance || [];
    
    // 生成策略详情HTML
    const rangeText = range === 'top8' ? '涨幅前8名' : '跌幅后8名';
    const directionText = direction === 'long' ? '做多' : '做空';
    const thresholdText = range === 'top8' ? '再涨' : '再跌';
    const directionIcon = direction === 'long' ? '📈' : '📉';
    
    // 币种列表
    let coinsListHTML = '<div class="mt-3 space-y-2">';
    targetCoins.forEach((coin, index) => {
        const changeColor = coin.change >= 0 ? 'text-green-600' : 'text-red-600';
        const changeSign = coin.change >= 0 ? '+' : '';
        coinsListHTML += `
            <div class="p-2 bg-white rounded border border-gray-200">
                <div class="font-semibold">${index + 1}. ${coin.symbol}</div>
                <div class="${changeColor} text-sm">${changeSign}${coin.change.toFixed(2)}%</div>
            </div>
        `;
    });
    coinsListHTML += '</div>';
    
    // 账户开仓建议
    let accountsHTML = '<div class="mt-4">';
    accountsHTML += '<h5 class="font-bold text-gray-800 mb-2">各账户建议开仓金额：</h5>';
    accountsHTML += '<div class="space-y-2">';
    
    if (accounts.length === 0 || !accounts[0].balance) {
        accountsHTML += `
            <div class="p-3 bg-yellow-100 rounded border border-yellow-300">
                <span class="text-yellow-800">⚠️ 未加载账户余额信息，请先刷新页面或配置账户</span>
            </div>
        `;
    } else {
        accounts.forEach(account => {
            if (account.balance && account.balance.availableBalance > 0) {
                const availBal = account.balance.availableBalance;
                const positionSize = availBal * (threshold / 100);
                const requiredMargin = positionSize / leverage;
                
                accountsHTML += `
                    <div class="p-3 bg-blue-50 rounded border border-blue-200">
                        <div class="font-semibold text-gray-800">${account.name}</div>
                        <div class="text-sm text-gray-600 mt-1">
                            可用余额: <strong>${availBal.toFixed(2)} USDT</strong>
                        </div>
                        <div class="text-sm text-blue-700 mt-1">
                            建议开仓: <strong>${positionSize.toFixed(2)} USDT</strong> 
                            (需保证金: ${requiredMargin.toFixed(2)} USDT)
                        </div>
                    </div>
                `;
            }
        });
    }
    
    accountsHTML += '</div></div>';
    
    // 显示完整策略
    document.getElementById('strategyDetails').innerHTML = `
        <div class="space-y-2">
            <div class="flex items-center space-x-2">
                <span class="font-bold">${directionIcon} ${directionText}</span>
                <span class="text-gray-500">|</span>
                <span>选择范围: <strong>${rangeText}</strong></span>
            </div>
            <div class="flex items-center space-x-2">
                <span>触发条件: 等待${thresholdText} <strong class="text-orange-600">${threshold}%</strong> 后开仓</span>
                <span class="text-gray-500">|</span>
                <span>杠杆: <strong class="text-purple-600">${leverage}x</strong></span>
            </div>
            <div class="mt-3">
                <strong>选中的币种（${targetCoins.length}个）:</strong>
                ${coinsListHTML}
            </div>
            ${accountsHTML}
            <div class="mt-3 p-3 bg-yellow-100 rounded border border-yellow-300">
                <strong class="text-yellow-800">📌 下一步操作:</strong>
                <p class="text-sm text-yellow-700 mt-1">
                    请前往 <a href="/okx-trading" class="underline font-semibold hover:text-yellow-900">OKX交易页面</a> 
                    根据各账户建议金额手动下单
                </p>
            </div>
        </div>
    `;
    
    document.getElementById('currentStrategy').classList.remove('hidden');
    document.getElementById('currentStrategy').scrollIntoView({ behavior: 'smooth', block: 'center' });
}
```

#### 3.3 页面加载时获取余额

```javascript
// 页面加载完成后
document.addEventListener('DOMContentLoaded', async function() {
    // ... 其他初始化代码 ...
    
    // 加载账户余额
    console.log('🔄 正在加载账户余额信息...');
    await loadAccountsBalance();
    console.log('✅ 账户余额加载完成');
});
```

### 4. 后端API实现

在`app.py`中添加账户余额查询接口：

```python
@app.route('/api/okx-trading/account-balance', methods=['POST'])
def get_account_balance():
    """获取OKX账户余额"""
    try:
        data = request.get_json()
        api_key = data.get('apiKey')
        api_secret = data.get('apiSecret')
        passphrase = data.get('passphrase')
        
        if not all([api_key, api_secret, passphrase]):
            return jsonify({
                'success': False,
                'error': 'API凭证不完整'
            })
        
        # OKX API配置
        base_url = 'https://www.okx.com'
        endpoint = '/api/v5/account/balance'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        # 请求参数
        params = {'ccy': 'USDT'}
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_endpoint = f"{endpoint}?{query_string}"
        
        # 签名
        message = timestamp + 'GET' + full_endpoint
        mac = hmac.new(
            api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        signature = base64.b64encode(mac.digest()).decode()
        
        # 请求头
        headers = {
            'OK-ACCESS-KEY': api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }
        
        # 发送请求
        response = requests.get(
            base_url + full_endpoint,
            headers=headers,
            timeout=10
        )
        result = response.json()
        
        if result.get('code') == '0' and result.get('data'):
            balance_data = result['data'][0]
            return jsonify({
                'success': True,
                'data': {
                    'totalEq': balance_data.get('totalEq', '0'),
                    'availBal': balance_data.get('availBal', '0')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('msg', '获取余额失败')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
```

## 📊 改进效果对比

### 改进前
```
触发条件: 等待再涨 1.5% 后开仓 | 杠杆: 10x

问题：
- 不知道每个账户应该开多少仓位
- 需要手动计算每个账户的开仓金额
- 容易出错或仓位不均衡
```

### 改进后
```
各账户建议开仓金额：

POIT (子账户)
可用余额: 3500.00 USDT
建议开仓: 52.50 USDT (需保证金: 5.25 USDT)

主账户
可用余额: 2000.00 USDT
建议开仓: 30.00 USDT (需保证金: 3.00 USDT)

测试账户
可用余额: 1000.00 USDT
建议开仓: 15.00 USDT (需保证金: 1.50 USDT)

优势：
✅ 每个账户有明确的开仓金额建议
✅ 根据各账户实际可用余额计算
✅ 显示所需保证金，便于风险评估
✅ 避免手动计算错误
```

## 🔧 实施步骤

### 第1步：添加后端API
```bash
# 在app.py中添加 /api/okx-trading/account-balance 接口
```

### 第2步：修改前端代码
```bash
# 在coin_change_tracker.html中：
# 1. 添加 loadAccountsBalance() 函数
# 2. 修改 applyStrategy() 函数
# 3. 在DOMContentLoaded中调用余额加载
```

### 第3步：测试验证
```bash
# 1. 重启Flask
# 2. 清除浏览器缓存
# 3. 点击策略按钮测试
# 4. 验证各账户金额显示正确
```

### 第4步：优化体验
```bash
# 1. 添加加载动画
# 2. 添加余额刷新按钮
# 3. 添加余额过期提示（如5分钟后提示重新加载）
```

## ⚠️ 注意事项

### 1. API限流
- OKX API有调用频率限制
- 建议缓存余额数据5分钟
- 避免频繁刷新

### 2. 安全性
- API凭证仅在前端临时存储
- 不要在日志中输出完整凭证
- 使用HTTPS传输

### 3. 精度控制
- USDT金额保留2位小数
- 开仓金额向下取整（避免超限）
- 最小开仓金额验证（OKX要求>=5 USDT）

### 4. 错误处理
- 账户余额获取失败时的降级方案
- 余额为0或不足时的提示
- 网络超时的重试机制

## 📈 预期收益

### 用户体验提升
- ⏱️ 节省计算时间：从手动计算→自动显示
- ✅ 减少错误：避免手动计算失误
- 📊 更清晰：直观显示各账户建议金额
- 🎯 更精准：基于实际可用余额计算

### 风险控制改善
- 每个账户按自身余额比例开仓
- 避免某个账户过度杠杆
- 保证金需求透明化
- 便于总仓位控制

## 🎯 下一步行动

### 立即可做
1. ✅ 创建后端API `/api/okx-trading/account-balance`
2. ✅ 修改前端策略显示函数
3. ✅ 测试多账户场景

### 后续优化
1. 📊 添加账户余额变化趋势图
2. ⚡ 实时余额自动刷新
3. 🔔 余额不足预警
4. 📱 移动端适配

---

**文档版本**：v1.0  
**创建时间**：2026-02-08  
**状态**：📝 待实施  
**优先级**：🔴 高（用户明确需求）
