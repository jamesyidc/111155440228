# 27币涨跌幅止盈 - 快速参考

## 🚀 一键启动

```bash
# 启动所有账户监控
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-main --interpreter python3 -- account_main
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-fangfang12 --interpreter python3 -- account_fangfang12
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-poit --interpreter python3 -- account_poit
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-poit-main --interpreter python3 -- account_poit_main
pm2 start source_code/okx_coin_change_tpsl_monitor.py --name okx-coin-change-tpsl-anchor --interpreter python3 -- account_anchor
pm2 save
```

## 📊 状态检查

```bash
# 查看所有服务
pm2 list | grep coin-change-tpsl

# 查看日志
pm2 logs okx-coin-change-tpsl-main --nostream --lines 20

# 查看配置
cat data/okx_tpsl_settings/account_main_coin_change_tpsl.jsonl | head -1 | jq

# 查看当前27币涨跌幅
tail -1 data/coin_change_tracker/coin_change_$(date -d '+8 hours' +%Y%m%d).jsonl | jq '.total_change, .beijing_time'
```

## ⚙️ 配置修改

### Web UI
https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/okx-coin-change-tpsl

### API
```bash
# 获取配置
curl "http://localhost:9002/api/okx-trading/coin-change-tpsl-settings/account_main" | jq

# 更新配置
curl -X POST "http://localhost:9002/api/okx-trading/coin-change-tpsl-settings/account_main" \
  -H "Content-Type: application/json" \
  -d '{
    "shortTakeProfitEnabled": true,
    "shortTakeProfitThreshold": 10.0,
    "longTakeProfitEnabled": true,
    "longTakeProfitThreshold": 15.0
  }'
```

## 🎯 关键配置

| 参数 | 说明 | 建议值 |
|------|------|--------|
| shortTakeProfitThreshold | 空单止盈阈值 | 5-15% |
| longTakeProfitThreshold | 多单止盈阈值 | 10-20% |
| shortTakeProfitEnabled | 空单止盈开关 | true/false |
| longTakeProfitEnabled | 多单止盈开关 | true/false |

## 🔍 监控逻辑

### 空单止盈
- **条件**: 27币涨跌幅之和 < -阈值
- **示例**: 阈值=10%，当涨跌幅=-11%时触发
- **动作**: 平空单 → 记录 → 通知

### 多单止盈
- **条件**: 27币涨跌幅之和 > +阈值
- **示例**: 阈值=15%，当涨跌幅=+16%时触发
- **动作**: 平多单 → 记录 → 通知

## 📂 文件位置

| 类型 | 位置 |
|------|------|
| 监控脚本 | `source_code/okx_coin_change_tpsl_monitor.py` |
| 配置文件 | `data/okx_tpsl_settings/{account_id}_coin_change_tpsl.jsonl` |
| 执行记录 | `data/okx_tpsl_settings/{account_id}_coin_change_tpsl_execution.jsonl` |
| 数据源 | `data/coin_change_tracker/coin_change_YYYYMMDD.jsonl` |
| 日志 | `/home/user/.pm2/logs/okx-coin-change-tpsl-{account}-out.log` |
| Web UI | `templates/okx_coin_change_tpsl.html` |

## 🛠️ 常用命令

```bash
# 重启服务
pm2 restart okx-coin-change-tpsl-main

# 停止服务
pm2 stop okx-coin-change-tpsl-main

# 查看执行记录
tail -f data/okx_tpsl_settings/account_main_coin_change_tpsl_execution.jsonl | jq

# 查看实时日志
pm2 logs okx-coin-change-tpsl-main --lines 50

# 查看当前市场数据
curl -s "http://localhost:9002/api/coin-change-tracker/latest" | jq '.total_change, .beijing_time, .up_coins, .down_coins'
```

## 💡 快速提示

1. **监控间隔**: 30秒检查一次
2. **防重复**: 每个持仓只执行一次止盈
3. **即时生效**: 配置更新后30秒内生效
4. **独立控制**: 空单和多单止盈可独立启用/禁用
5. **自动重启**: PM2自动重启崩溃的服务

## 📞 故障排查

```bash
# 1. 检查服务是否运行
pm2 list | grep coin-change-tpsl

# 2. 检查配置文件是否存在
ls -lh data/okx_tpsl_settings/*coin_change_tpsl.jsonl

# 3. 检查数据采集是否正常
ls -lh data/coin_change_tracker/coin_change_$(date -d '+8 hours' +%Y%m%d).jsonl

# 4. 查看错误日志
pm2 logs okx-coin-change-tpsl-main --err --lines 50

# 5. 测试API
curl "http://localhost:9002/api/okx-trading/coin-change-tpsl-settings/account_main"
```

---

**创建日期**: 2026-03-02  
**状态**: ✅ 生产环境运行中  
**详细文档**: [COIN_CHANGE_TPSL_ACTIVATION_20260302.md](COIN_CHANGE_TPSL_ACTIVATION_20260302.md)
