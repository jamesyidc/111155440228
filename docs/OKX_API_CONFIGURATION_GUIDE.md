# OKX API配置说明 - 开仓失败问题解决

## 🚨 当前问题

**错误提示**：
```
STX: All operations failed (代码1)
CRV: All operations failed (代码1)
NEAR: All operations failed (代码1)
CFX: All operations failed (代码1)
UNI: All operations failed (代码1)
XLM: All operations failed (代码1)
```

**原因**：未配置OKX API密钥，或API密钥配置不正确

---

## ✅ 解决方案

### 1. 获取OKX API密钥

#### 步骤1：登录OKX账户
访问：https://www.okx.com/

#### 步骤2：创建API密钥
1. 进入 **账户设置** → **API管理**
2. 点击 **创建API**
3. 选择API权限：
   - ✅ **读取** (Read)
   - ✅ **交易** (Trade) - **必须开启！**
   - ❌ 提现 (Withdraw) - 建议不开启

#### 步骤3：记录API信息
创建后会得到3个关键信息：
- **API Key** (例如：xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
- **Secret Key** (例如：xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
- **Passphrase** (你设置的密码短语)

⚠️ **重要提示**：Secret Key只会显示一次，请妥善保存！

---

### 2. 在系统中配置API密钥

#### 方法A：前端页面配置（推荐）

1. 访问页面：
   ```
   https://5000-ikmpd2up5chrwx4jjjkih-5634da27.sandbox.novita.ai/anchor-system-real
   ```

2. 找到**API设置**区域（通常在顶部或设置菜单）

3. 填入API信息：
   - API Key: `[你的API Key]`
   - Secret Key: `[你的Secret Key]`
   - Passphrase: `[你的Passphrase]`

4. 点击**保存配置**

#### 方法B：配置文件方式

创建配置文件：`/home/user/webapp/configs/okx_api_config.json`

```json
{
  "api_key": "你的API_KEY",
  "secret_key": "你的SECRET_KEY",
  "passphrase": "你的PASSPHRASE",
  "base_url": "https://www.okx.com",
  "trade_mode": "real"
}
```

**设置权限**：
```bash
chmod 600 /home/user/webapp/configs/okx_api_config.json
```

---

### 3. 验证API配置

#### 测试API连接
```bash
curl -X POST http://localhost:5000/api/okx/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "你的API_KEY",
    "apiSecret": "你的SECRET_KEY",
    "passphrase": "你的PASSPHRASE"
  }'
```

#### 预期返回
```json
{
  "success": true,
  "message": "API连接成功",
  "account_info": {...}
}
```

---

## 🔧 开仓功能配置检查

### 必需权限
- ✅ **交易权限** (Trade) - 必须开启
- ✅ **读取权限** (Read) - 必须开启
- ✅ **永续合约交易** - 必须开启

### 杠杆设置
- 默认杠杆：10x
- 保证金模式：逐仓 (Isolated)
- 可以在开仓时调整杠杆倍数

### 开仓参数
每次开仓需要以下信息：
- **交易对** (instId): 如 BTC-USDT-SWAP
- **方向** (side): buy (开多) / sell (开空)
- **仓位方向** (posSide): long (做多) / short (做空)
- **数量** (sz): USDT金额
- **订单类型** (ordType): market (市价) / limit (限价)
- **杠杆** (lever): 默认10x

---

## 🚨 常见错误及解决

### 错误1：API凭证不完整
```
错误: API凭证不完整
```
**解决**：检查API Key、Secret Key、Passphrase都已正确填写

### 错误2：API权限不足
```
错误: 权限不足 (code: 50111)
```
**解决**：确认API已开启"交易"权限

### 错误3：IP白名单
```
错误: IP地址未授权 (code: 50113)
```
**解决**：
1. 进入OKX API设置
2. 添加服务器IP到白名单
3. 或设置为"不限制IP"（测试环境）

### 错误4：签名错误
```
错误: Invalid signature (code: 50100)
```
**解决**：
1. 检查Secret Key是否正确
2. 确认时间戳是否准确
3. 重新生成API密钥

---

## 📊 安全建议

### API密钥安全
1. ✅ **不要泄露**：不要将API密钥提交到Git仓库
2. ✅ **定期更换**：每月更换一次API密钥
3. ✅ **限制权限**：只开启必要的权限
4. ✅ **IP白名单**：生产环境务必设置IP白名单
5. ✅ **专用密钥**：不同系统使用不同的API密钥

### 资金安全
1. ✅ **测试账户**：先用模拟盘测试
2. ✅ **小额测试**：实盘先用小额测试
3. ✅ **止损设置**：设置合理的止损点
4. ✅ **仓位管理**：不要满仓操作
5. ✅ **监控告警**：配置Telegram通知

---

## 🎯 开仓流程

### 正常开仓流程
1. **配置API** → 填写API密钥
2. **选择币种** → 勾选要开仓的币种
3. **设置参数** → 设置杠杆、金额
4. **批量开仓** → 点击"批量开仓A"或"批量开仓B"
5. **确认订单** → 查看订单详情
6. **执行开仓** → 确认后执行
7. **监控持仓** → 查看持仓情况

### 开仓失败排查
1. ✅ 检查API配置是否正确
2. ✅ 检查网络连接
3. ✅ 检查币种是否可交易
4. ✅ 检查账户余额是否充足
5. ✅ 检查杠杆设置是否合理
6. ✅ 查看Flask日志获取详细错误

---

## 📞 获取帮助

### 查看日志
```bash
# Flask应用日志
pm2 logs flask-app --lines 100

# 查看错误日志
pm2 logs flask-app --err --lines 50

# 实时查看日志
pm2 logs flask-app
```

### 调试模式
在Flask应用中添加调试日志，查看API调用详情

---

## ✅ 配置完成检查清单

- [ ] 已在OKX创建API密钥
- [ ] API密钥已开启"交易"权限
- [ ] 已在系统中配置API密钥
- [ ] 已测试API连接成功
- [ ] 已测试小额开仓成功
- [ ] 已配置Telegram通知（可选）
- [ ] 已设置止损策略
- [ ] 已了解风险提示

---

## ⚠️ 风险提示

**加密货币交易存在极高风险，可能导致本金全部损失！**

1. 永续合约使用杠杆，风险远高于现货
2. 极端行情可能导致爆仓
3. 自动化交易系统可能出现故障
4. 网络延迟可能影响交易执行
5. 请只使用可承受损失的资金

**在使用本系统前，请确保你完全理解相关风险！**

---

**需要帮助？**
如果API配置后仍然无法开仓，请提供：
1. 完整的错误信息
2. Flask应用日志
3. API配置方式（前端/配置文件）
4. 尝试开仓的币种和参数
