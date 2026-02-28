# 27币追踪系统 - 重新部署流程总结

## 📋 核心流程

### 1. 在旧系统导出数据

```bash
cd /home/user/webapp
./migrate_coin_tracker.sh export
```

**会发生什么**:
- 停止 `coin-change-tracker` 采集器
- 导出所有JSONL文件 (约112MB)
- 生成备份文件: `coin_tracker_backup_YYYYMMDD_HHMMSS.json`
- 重启采集器

### 2. 传输备份文件

将生成的备份文件传输到新系统:
- 方式1: 下载后手动上传
- 方式2: 通过API直接传输
- 方式3: Git仓库存储

### 3. 在新系统导入数据

```bash
cd /home/user/webapp
./migrate_coin_tracker.sh import coin_tracker_backup_20260224_133000.json
```

**会发生什么**:
- 创建数据目录
- 备份现有数据 (如果有)
- 导入所有文件
- 启动 `coin-change-tracker` PM2进程
- 重启 `flask-app`
- 执行健康检查

### 4. 验证系统正常

访问: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker

检查:
- ✅ 27个币种涨跌数据实时显示
- ✅ RSI之和曲线 (灰色粗线)
- ✅ 波峰标记 (B点/A点/C点)
- ✅ 暴跌预警卡片功能

---

## 📊 数据说明

### 数据目录结构

```
/home/user/webapp/data/
├── coin_change_tracker/
│   ├── coin_change_20260201.jsonl    # 2.3 MB - 每日涨跌数据
│   ├── coin_change_20260202.jsonl    # 1.9 MB
│   ├── ...                           # (共35个文件)
│   ├── rsi_20260201.jsonl            # 100 KB - RSI指标
│   ├── rsi_20260202.jsonl            # 130 KB
│   ├── ...
│   ├── baseline_20260201.json        # 1 KB - 基线价格
│   ├── baseline_20260202.json        # 1 KB
│   └── ...
└── crash_warning_events/
    └── february_analysis.json        # 2月份预警分析
```

**总数据量**: 约112MB

### 数据类型详解

#### 1. 币种涨跌数据 (coin_change_YYYYMMDD.jsonl)

每分钟记录一次，每天约1440条记录。

格式示例:
```json
{
  "timestamp": "2026-02-24T13:06:00+08:00",
  "BTC": -1.23,
  "ETH": 0.45,
  "BNB": -0.12,
  "XRP": 2.34,
  ... (共27个币种)
}
```

#### 2. RSI指标数据 (rsi_YYYYMMDD.jsonl)

14周期RSI值，用于绘制"RSI之和"曲线。

格式示例:
```json
{
  "timestamp": "2026-02-24T13:06:00+08:00",
  "BTC_rsi": 65.4,
  "ETH_rsi": 52.3,
  ... (共27个币种_rsi)
}
```

#### 3. 基线价格 (baseline_YYYYMMDD.json)

每天北京时间02:00更新一次，作为当天涨跌幅计算的基准。

格式示例:
```json
{
  "date": "20260224",
  "timestamp": "2026-02-24T02:00:00+08:00",
  "BTC": 98765.43,
  "ETH": 3456.78,
  ... (27个币种基线价格)
}
```

---

## 🔧 PM2进程说明

### 币种追踪采集器

**进程名**: `coin-change-tracker`  
**脚本**: `/home/user/webapp/source_code/coin_change_tracker_collector.py`  
**功能**: 
- 每分钟采集27个币种价格
- 计算相对基线的涨跌幅
- 计算14周期RSI指标
- 写入JSONL文件

**启动命令**:
```bash
pm2 start source_code/coin_change_tracker_collector.py \
  --name coin-change-tracker \
  --interpreter python3 \
  --cron-restart="0 2 * * *"
```

**Cron重启**: 每天02:00自动重启 (同时更新基线价格)

### 监控命令

```bash
# 查看服务状态
pm2 list | grep coin

# 查看实时日志
pm2 logs coin-change-tracker --lines 0

# 重启服务
pm2 restart coin-change-tracker

# 查看内存使用
pm2 monit
```

---

## ⚙️ 系统依赖

### Python包

```bash
pip3 install requests numpy pytz
```

### Node.js工具

数据同步脚本依赖:
- `scripts/export_daily_data.js` - 数据导出
- `scripts/import_daily_data.js` - 数据导入

---

## 📈 2月份数据分析结果

### 暴跌预警统计

**分析脚本**: `scripts/check_february_crash_warnings.py`

**结果** (已修复bug后):
- 总天数: 24天
- 有效数据: 23天
- 预警天数: 8天
- **预警率: 34.8%**

**预警日期**:
1. 2026-02-04 - A点递减模式
2. 2026-02-05 - A点递减（A1 > A2 > A3）
3. **2026-02-06** - A点递减模式 (5个波峰)
4. 2026-02-07 - A点递减（A1 > A2 > A3）
5. 2026-02-09 - A点递减（A1 > A2 > A3）

**查看详细分析**:
```bash
cat data/crash_warning_events/february_analysis.json | jq '.'
```

---

## 🐛 已修复的Bug

### Bug #1: 波峰检测返回值未正确解包

**问题**: `detect_wave_peaks()` 返回 `(peaks, current_state)` 元组，但代码只接收了一个变量，导致类型错误。

**修复**: PR #1, Commit `b74fb45`

```python
# 修复前
peaks = detector.detect_wave_peaks(data)

# 修复后
peaks, current_state = detector.detect_wave_peaks(data)
```

**影响**: 修复后，2月份从0天预警变为8天预警 (34.8%)

### Bug #2: RSI之和曲线不显示

**问题**: 前端代码中RSI曲线配置错误，导致线条不显示或显示为细线。

**修复**: PR #1, Commit `bf99b2b`

**改进**:
- 线宽: 1px → 3px
- z-index: 默认 → 10
- 颜色: 灰色 (#808080)

---

## 📚 完整文档索引

| 文档 | 用途 | 阅读时间 |
|------|------|---------|
| `DEPLOYMENT_QUICK_REF.md` | 快速参考 | 3分钟 |
| `DEPLOYMENT_DATA_MIGRATION_GUIDE.md` | 完整指南 | 15分钟 |
| `DATA_SYNC_GUIDE.md` | 数据同步系统 | 10分钟 |
| `DATA_SYNC_QUICK_REF.md` | 同步工具快速参考 | 5分钟 |

---

## 🎯 一键命令速查

```bash
# 导出数据
./migrate_coin_tracker.sh export

# 导入数据
./migrate_coin_tracker.sh import backup.json

# 查看帮助
./migrate_coin_tracker.sh help

# 查看服务
pm2 list

# 查看日志
pm2 logs coin-change-tracker

# 重启服务
pm2 restart coin-change-tracker

# 分析2月数据
python3 scripts/check_february_crash_warnings.py

# 查看分析结果
cat data/crash_warning_events/february_analysis.json | jq '.'
```

---

## 🌐 相关链接

- **Web界面**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
- **GitHub**: https://github.com/jamesyidc/1212335551
- **PR #1**: https://github.com/jamesyidc/1212335551/pull/1

---

**版本**: v1.0  
**更新**: 2026-02-24  
**作者**: GenSpark AI Developer  
**状态**: ✅ 生产就绪
