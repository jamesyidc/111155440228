# Git提交待办事项

**状态**: ⚠️ Git进程遇到问题，需要手动提交

## 问题描述
- Git命令遇到 Bus error
- 可能是Git索引损坏

## 需要提交的文件

### 后端文件
1. `source_code/app_new.py`
   - 新增API：/api/sar-slope/bias-trend-by-date
   - 修改API：/api/okx-trading/place-order（添加止盈止损）
   - 新增API：/api/okx-trading/set-tpsl

2. `source_code/sar_1min_collector.py`
   - 修改：TAO使用SWAP交易对

3. `source_code/sar_jsonl_collector.py`
   - 修改：TAO使用SWAP交易对

### 前端文件
1. `source_code/templates/sar_bias_trend.html`
   - 完全重构：按日期查看模式
   - 新增：健康监控面板

2. `source_code/templates/okx_trading.html`
   - 新增：止盈止损输入框
   - 新增：批量设置止盈止损控件

### 文档文件
1. `SAR_BIAS_DATE_VIEW_REPORT.md`
2. `SUI_TAO_FIX_REPORT.md`
3. `SAR_BIAS_HEALTH_MONITOR_REPORT.md`
4. `OKX_TPSL_FEATURE_REPORT.md`
5. `SESSION_COMPLETE_REPORT.md`
6. `d7SLtVq1.png`（截图）
7. `GIT_COMMIT_TODO.md`（本文件）

## 建议的提交消息

```
feat: SAR偏向按日期查看+SUI/TAO修复+健康监控+OKX止盈止损

主要改动：
1. SAR偏向趋势图 - 按日期查看功能
   - 新增日期选择控件
   - 新增 /api/sar-slope/bias-trend-by-date API
   - 完全重构前端页面

2. SUI和TAO数据采集修复
   - TAO使用永续合约 TAO-USDT-SWAP
   - 采集成功率提升至100% (27/27)

3. 数据采集健康监控功能
   - 6项实时监控指标
   - 自动状态判断和告警

4. OKX交易系统止盈止损功能
   - 下单时设置止盈止损百分比
   - 持仓批量设置止盈止损
   - 新增 /api/okx-trading/set-tpsl API

测试状态：
- SAR采集：✅ 27/27成功
- 健康监控：✅ 正常运行
- OKX止盈止损：⚠️ 待真实交易测试
```

## 手动提交步骤

### 方法1：使用新的shell会话
```bash
cd /home/user/webapp

# 清理可能损坏的索引
rm -f .git/index
rm -f .git/index.lock

# 重新添加文件
git add source_code/app_new.py
git add source_code/sar_1min_collector.py
git add source_code/sar_jsonl_collector.py
git add source_code/templates/sar_bias_trend.html
git add source_code/templates/okx_trading.html
git add *.md
git add d7SLtVq1.png

# 提交
git commit -m "feat: SAR偏向按日期查看+SUI/TAO修复+健康监控+OKX止盈止损"

# 推送
git push origin genspark_ai_developer
```

### 方法2：重新初始化Git（不推荐）
如果上述方法失败，可以考虑重新clone仓库并手动复制文件。

## 系统当前状态

### 采集器状态（所有正常）
- ✅ sar-1min-collector: 在线
- ✅ sar-jsonl-collector: 在线
- ✅ sar-bias-stats-collector: 在线
- ✅ flask-app: 在线

### 数据采集健康状况
- 成功率：100% (27/27)
- 最后采集：16:08:38
- 延迟：<3分钟
- 失败币种：无

### 功能访问链接
1. SAR偏向趋势图：https://5000-ikmpd2up5chrwx4jjjjih-5634da27.sandbox.novita.ai/sar-bias-trend
2. OKX交易系统：https://5000-ikmpd2up5chrwx4jjjkih-5634da27.sandbox.novita.ai/okx-trading

## 备注
- 所有功能已开发完成并在线运行
- 代码改动已保存到文件系统
- 仅Git提交步骤待完成
- 建议在新的shell会话中尝试提交
