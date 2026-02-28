# OKX自动策略仓位配置快速指南

## 🎯 如何调整仓位百分比

### 1. 编辑配置文件
```bash
cd /home/user/webapp/data/okx_auto_strategy
vim account_poit_main.json
```

### 2. 修改 positionSize 字段
```json
{
  "enabled": true,
  "triggerPrice": 67000.0,
  "strategyType": "bottom_performers",
  "positionSize": 1.5,    ← 修改这个值
  ...
}
```

### 3. 保存后自动生效（下次触发时）

## 📊 推荐配置

| 风险等级 | positionSize | 每币开仓* | 说明 |
|---------|--------------|----------|------|
| 🟢 保守 | 0.5% | 0.99 U | 适合测试/小资金 |
| 🟡 稳健 | 1.5% | 2.98 U | **推荐配置** |
| 🔴 激进 | 3.0% | 5.00 U | 注意风险 |

*基于总权益 198.64 USDT 计算

## ⚠️ 重要提示

1. **上限保护**：单笔最多 5 USDT
2. **使用总权益**：计算基于 totalEquity，不是可用余额
3. **8币总计**：实际使用 = 每币开仓 × 8
4. **风险控制**：建议不超过总权益的20%

## 🔍 验证配置

下次策略触发后，查看日志：
```bash
pm2 logs flask-app --lines 20 | grep "开仓金额"
```

预期输出：
```
📊 每个币种开仓金额: 2.98 USDT (总权益198.64 × 1.5%, 上限5U)
```

## 📞 问题排查

配置未生效？检查：
1. JSON格式是否正确
2. 策略是否已触发
3. Flask应用是否重启

重启Flask：
```bash
pm2 restart flask-app
```
