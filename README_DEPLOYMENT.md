# 27币追踪系统 - 重新部署完整方案

> 🎯 **核心功能**: 补齐部署期间缺失的1-2小时数据，确保数据完整性

---

## 📋 问题场景

重新部署27币追踪系统时，通常需要1-2小时：

```
14:00 - 停止采集器 (旧系统)
14:05 - 备份数据
14:25 - 传输文件
14:50 - 部署系统
15:10 - 启动服务 (新系统)
15:15 - 开始采集 ✓
```

**数据缺失**: 14:00 - 15:15 (1小时15分钟) ❌

---

## ✅ 解决方案

### 🚀 一键补齐 (3步完成)

#### 步骤1: 完成重新部署

```bash
cd /home/user/webapp
./migrate_coin_tracker.sh import backup.json
```

#### 步骤2: 补齐缺失数据

```bash
cd /home/user/webapp
./quick_backfill.sh --last-2h
```

#### 步骤3: 验证数据完整

```bash
# 查看今日数据
tail -10 data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 访问Web界面
# https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
```

**完成！** ✨ 数据已补齐，系统正常运行。

---

## 📖 详细功能

### 1️⃣ 数据迁移工具

**脚本**: `migrate_coin_tracker.sh`  
**用途**: 备份和恢复历史数据

```bash
# 在旧系统导出
./migrate_coin_tracker.sh export

# 在新系统导入
./migrate_coin_tracker.sh import backup.json
```

**数据内容**:
- 币种涨跌数据 (coin_change_*.jsonl)
- RSI指标数据 (rsi_*.jsonl)
- 基线价格 (baseline_*.json)
- 暴跌预警记录

**文档**: `DEPLOYMENT_DATA_MIGRATION_GUIDE.md`

---

### 2️⃣ 数据补齐工具 ⭐ NEW

**脚本**: `quick_backfill.sh`  
**用途**: 补齐部署期间缺失的当天数据

#### 快速模式

```bash
# 补齐最近2小时（推荐）
./quick_backfill.sh --last-2h

# 补齐最近1小时
./quick_backfill.sh --last-1h
```

#### 自定义模式

```bash
# 补齐13:00到15:30的数据
./quick_backfill.sh --custom 13:00 15:30
```

#### 交互式模式

```bash
# 手动输入时间范围
./quick_backfill.sh
```

**工作原理**:
1. 从OKX历史K线API获取1分钟数据
2. 计算相对基线的涨跌幅
3. 计算14周期RSI指标
4. 写入JSONL文件（智能跳过已有时间戳）

**限制**:
- 最大补齐5小时（API限制）
- 仅补齐当天数据
- 需要基线文件存在

**文档**: `DATA_BACKFILL_GUIDE.md`

---

## 🎯 完整部署流程

### 标准流程 (推荐)

```bash
# ========== 旧系统操作 ==========
cd /home/user/webapp

# 1. 导出数据
./migrate_coin_tracker.sh export
# 输出: coin_tracker_backup_20260224_140000.json

# 2. 记录停止时间
STOP_TIME=$(date '+%H:%M')
echo "停止时间: $STOP_TIME"  # 例如: 14:00

# ========== 传输文件到新系统 ==========

# ========== 新系统操作 ==========
cd /home/user/webapp

# 3. 导入数据
./migrate_coin_tracker.sh import coin_tracker_backup_20260224_140000.json

# 4. 补齐缺失数据
./quick_backfill.sh --last-2h

# 5. 验证系统
pm2 list
pm2 logs coin-change-tracker --lines 20
tail -10 data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl
```

### 快速流程 (适合测试)

```bash
# 新系统上，一键执行
cd /home/user/webapp
./migrate_coin_tracker.sh import backup.json && ./quick_backfill.sh --last-2h
```

---

## 📊 数据说明

### 数据类型

| 文件类型 | 示例 | 大小 | 频率 |
|---------|------|------|------|
| 币种涨跌 | `coin_change_20260224.jsonl` | 2-4 MB | 每分钟 |
| RSI指标 | `rsi_20260224.jsonl` | 100-130 KB | 每分钟 |
| 基线价格 | `baseline_20260224.json` | ~1 KB | 每日02:00 |
| 暴跌预警 | `crash_warning_events/*.json` | 可变 | 按需 |

### 数据目录

```
/home/user/webapp/data/
├── coin_change_tracker/       # 主数据目录 (~112MB)
│   ├── coin_change_20260224.jsonl
│   ├── rsi_20260224.jsonl
│   └── baseline_20260224.json
└── crash_warning_events/       # 预警数据
    └── february_analysis.json
```

### 币种列表 (27个)

```
BTC, ETH, BNB, XRP, DOGE, SOL, DOT, MATIC, LTC, LINK,
HBAR, TAO, CFX, TRX, TON, NEAR, LDO, CRO, ETC, XLM,
BCH, UNI, SUI, FIL, STX, CRV, AAVE, APT
```

---

## 🔧 系统管理

### PM2服务

```bash
# 查看服务状态
pm2 list | grep coin

# 查看实时日志
pm2 logs coin-change-tracker --lines 0

# 重启服务
pm2 restart coin-change-tracker

# 停止服务
pm2 stop coin-change-tracker
```

### 数据检查

```bash
# 统计今日数据行数
wc -l data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 查看最新记录
tail -5 data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 检查数据目录大小
du -sh data/coin_change_tracker/
```

### 健康检查

```bash
# 检查采集器运行
pm2 list | grep -E "coin-change-tracker.*online"

# 检查数据更新
ls -lt data/coin_change_tracker/coin_change_*.jsonl | head -3

# 查看最新时间戳
tail -1 data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl | jq -r '.timestamp'
```

---

## 📚 文档索引

### 核心文档

| 文档 | 说明 | 阅读时间 |
|------|------|---------|
| **README_DEPLOYMENT.md** (本文档) | 总体说明 | 5分钟 |
| **DATA_BACKFILL_GUIDE.md** | 数据补齐详细指南 | 10分钟 |
| **DEPLOYMENT_DATA_MIGRATION_GUIDE.md** | 完整迁移流程 | 15分钟 |
| **DEPLOYMENT_QUICK_REF.md** | 快速参考 | 3分钟 |
| **DEPLOYMENT_SUMMARY.md** | 系统架构总结 | 5分钟 |

### 其他文档

- `DATA_SYNC_GUIDE.md` - 数据同步系统
- `DATA_SYNC_QUICK_REF.md` - 同步工具参考
- `DATA_SYNC_DEVELOPMENT_REPORT.md` - 开发报告

---

## 🎯 快速命令参考

```bash
# ========== 数据迁移 ==========
./migrate_coin_tracker.sh export           # 导出数据
./migrate_coin_tracker.sh import backup.json  # 导入数据

# ========== 数据补齐 ==========
./quick_backfill.sh --last-2h              # 补齐最近2小时
./quick_backfill.sh --last-1h              # 补齐最近1小时
./quick_backfill.sh --custom 13:00 15:30   # 自定义时间范围
./quick_backfill.sh                        # 交互式输入

# ========== 系统管理 ==========
pm2 list                                   # 查看服务
pm2 logs coin-change-tracker               # 查看日志
pm2 restart coin-change-tracker            # 重启服务

# ========== 数据验证 ==========
tail -f data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl
wc -l data/coin_change_tracker/*.jsonl
du -sh data/coin_change_tracker/
```

---

## ⚠️ 注意事项

### 数据补齐前提

1. ✅ 基线文件必须存在: `baseline_YYYYMMDD.json`
2. ✅ Python环境正常: `python3 --version`
3. ✅ 依赖包已安装: `pip3 install requests numpy pytz`

### 常见问题

#### Q1: 基线文件不存在？

```bash
# 检查基线文件
ls -lh data/coin_change_tracker/baseline_$(date +%Y%m%d).json

# 如果不存在
# - 等待每天02:00自动生成
# - 或从旧系统复制
```

#### Q2: Python依赖缺失？

```bash
# 安装依赖
pip3 install requests numpy pytz

# 验证
python3 -c "import requests, numpy, pytz; print('OK')"
```

#### Q3: 数据补齐失败？

```bash
# 查看详细日志
./quick_backfill.sh --last-1h 2>&1 | tee backfill.log

# 检查网络
curl -I https://www.okx.com/api/v5/market/candles

# 手动测试
python3 scripts/backfill_today_data.py
```

---

## 🌐 系统链接

- **Web界面**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
- **GitHub仓库**: https://github.com/jamesyidc/1212335551
- **当前PR**: https://github.com/jamesyidc/1212335551/pull/1

---

## 🔖 版本历史

### v1.0 - 2026-02-24

**新增功能**:
- ✅ 数据迁移工具 (`migrate_coin_tracker.sh`)
- ✅ 数据补齐工具 (`quick_backfill.sh`)
- ✅ 完整文档体系
- ✅ 2月份数据分析 (8天预警, 34.8%)

**关键修复**:
- ✅ 波峰检测bug (Commit b74fb45)
- ✅ RSI曲线显示问题 (Commit bf99b2b)

**文档**:
- ✅ 5份核心文档
- ✅ 详细的使用案例
- ✅ 命令速查表

---

## 📞 技术支持

如有问题，请参考相关文档或在GitHub提Issue。

**最后更新**: 2026-02-24  
**状态**: ✅ 生产就绪  
**维护者**: GenSpark AI Developer
