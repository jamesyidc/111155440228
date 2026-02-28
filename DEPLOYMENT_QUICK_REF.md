# 27币追踪系统 - 重新部署快速参考

> **快速上手**: 5分钟完成数据迁移

---

## 🚀 一键迁移 (推荐)

### 旧系统 → 导出数据

```bash
cd /home/user/webapp
./migrate_coin_tracker.sh export
```

**输出文件**: `coin_tracker_backup_YYYYMMDD_HHMMSS.json`

### 新系统 → 导入数据

```bash
cd /home/user/webapp
./migrate_coin_tracker.sh import coin_tracker_backup_20260224_133000.json
```

**完成**: 访问 https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker

---

## 📊 数据概览

### 数据类型

| 文件类型 | 命名格式 | 大小 | 说明 |
|---------|---------|------|------|
| 币种涨跌 | `coin_change_YYYYMMDD.jsonl` | 2-4 MB | 每分钟记录27个币种涨跌幅 |
| RSI指标 | `rsi_YYYYMMDD.jsonl` | 100-130 KB | 14周期RSI指标 |
| 基线价格 | `baseline_YYYYMMDD.json` | ~1 KB | 每日02:00更新基线 |
| 暴跌预警 | `crash_warning_events/*.json` | 可变 | 波峰检测与预警记录 |

### 数据位置

```
/home/user/webapp/data/
├── coin_change_tracker/          # 币种追踪数据 (~112MB)
│   ├── coin_change_20260201.jsonl
│   ├── coin_change_20260202.jsonl
│   ├── rsi_20260201.jsonl
│   ├── rsi_20260202.jsonl
│   ├── baseline_20260201.json
│   └── baseline_20260202.json
└── crash_warning_events/          # 暴跌预警数据
    └── february_analysis.json
```

---

## 🔧 手动迁移 (备选)

### 方案A: 使用数据同步工具

```bash
# 导出
cd /home/user/webapp
node scripts/export_daily_data.js http://localhost:9002 backup.json

# 导入
cd /home/user/webapp
node scripts/import_daily_data.js http://localhost:9002 backup.json
```

### 方案B: 手动打包

```bash
# 旧系统: 打包
cd /home/user/webapp
tar -czf coin_data_$(date +%Y%m%d).tar.gz \
  data/coin_change_tracker/*.jsonl \
  data/coin_change_tracker/baseline_*.json \
  data/crash_warning_events/

# 新系统: 解压
cd /home/user/webapp
tar -xzf coin_data_20260224.tar.gz
```

---

## ⚙️ PM2 服务管理

### 查看服务状态

```bash
pm2 list | grep coin
```

### 启动币种追踪器

```bash
cd /home/user/webapp
pm2 start source_code/coin_change_tracker_collector.py \
  --name coin-change-tracker \
  --interpreter python3 \
  --cron-restart="0 2 * * *"
```

### 查看实时日志

```bash
pm2 logs coin-change-tracker --lines 0
```

### 重启服务

```bash
pm2 restart coin-change-tracker
pm2 restart flask-app
```

---

## ✅ 验证清单

### 数据完整性

```bash
# 统计文件数量
ls -1 data/coin_change_tracker/*.jsonl | wc -l    # 应该 ≈35

# 查看最新数据
ls -lt data/coin_change_tracker/coin_change_*.jsonl | head -3

# 检查文件大小
du -sh data/coin_change_tracker/                  # 应该 ≈112MB
```

### 服务运行状态

```bash
# 确认服务在线
pm2 list | grep -E "coin-change-tracker.*online"
pm2 list | grep -E "flask-app.*online"

# 检查数据更新
tail -f data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl
```

### Web界面检查

访问: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker

- [ ] 27个币种实时涨跌数据显示
- [ ] RSI之和曲线正常 (灰色粗线, 3px宽度)
- [ ] 波峰标记正确 (B点绿色, A点橙色, C点灰色)
- [ ] 暴跌预警卡片可折叠
- [ ] 时间戳实时更新

---

## 🔍 常见问题

### Q1: 数据采集器未启动

```bash
# 查看错误日志
pm2 logs coin-change-tracker --err --lines 50

# 检查Python依赖
pip3 list | grep -E "requests|numpy|pytz"

# 重新启动
pm2 delete coin-change-tracker
pm2 start source_code/coin_change_tracker_collector.py \
  --name coin-change-tracker --interpreter python3
```

### Q2: RSI曲线不显示

**原因**: PR #1 (Commit bf99b2b) 已修复此问题

```bash
# 确认修复已合并
git log --oneline | grep -i "rsi"

# 清除浏览器缓存，强制刷新 (Ctrl+Shift+R)
```

### Q3: 暴跌预警未触发

**原因**: PR #1 (Commit b74fb45) 修复了波峰检测逻辑

```bash
# 运行2月份完整分析
python3 scripts/check_february_crash_warnings.py

# 查看结果
cat data/crash_warning_events/february_analysis.json | jq '.'
```

**预期结果**: 2月份8天预警 (34.8%预警率)

### Q4: 数据文件未更新

```bash
# 1. 确认进程运行
pm2 list | grep coin-change-tracker

# 2. 查看实时日志
pm2 logs coin-change-tracker --lines 0

# 3. 手动测试采集
python3 source_code/coin_change_tracker_collector.py
```

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| `DEPLOYMENT_DATA_MIGRATION_GUIDE.md` | 完整迁移指南 (15分钟详细步骤) |
| `DATA_SYNC_GUIDE.md` | 数据同步系统文档 |
| `DATA_SYNC_QUICK_REF.md` | 数据同步快速参考 |
| `README.md` | 项目总体说明 |

---

## 🎯 核心命令速查

```bash
# 【导出数据】
./migrate_coin_tracker.sh export

# 【导入数据】
./migrate_coin_tracker.sh import backup.json

# 【查看服务】
pm2 list

# 【查看日志】
pm2 logs coin-change-tracker

# 【重启服务】
pm2 restart coin-change-tracker

# 【查看最新数据】
tail -f data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 【运行分析】
python3 scripts/check_february_crash_warnings.py

# 【查看分析结果】
cat data/crash_warning_events/february_analysis.json | jq '.'
```

---

## 🌐 系统链接

- **Web界面**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
- **GitHub仓库**: https://github.com/jamesyidc/1212335551
- **当前PR**: https://github.com/jamesyidc/1212335551/pull/1

---

## 📞 技术支持

如有问题，请参考完整文档 `DEPLOYMENT_DATA_MIGRATION_GUIDE.md` 或在GitHub提Issue。

---

**版本**: v1.0  
**更新**: 2026-02-24  
**状态**: ✅ 生产就绪
