# 锚点系统按日期存储修复报告

## 修复时间
2026-01-28

## 问题描述
1. **多空单盈利统计数据**：原来所有数据存储在单个 `anchor_profit_stats.jsonl` 文件中，随着时间增长文件越来越大，加载缓慢
2. **历史极值记录数据**：原来所有数据存储在单个 `extreme_real.jsonl` 文件中，且该文件损坏无法读取
3. **前端加载问题**：每次都加载全部历史数据，导致页面加载缓慢

## 修复方案

### 1. 多空单盈利统计 - 按日期存储
**数据目录**：`/home/user/webapp/data/anchor_daily/`

**文件命名**：`anchor_data_YYYY-MM-DD.jsonl` 和 `.jsonl.gz`（压缩版）

**实现**：
- 创建 `AnchorDailyReader` 类，支持按日期读取数据
- API `/api/anchor-profit/by-date` 支持 `date` 参数（YYYY-MM-DD格式）
- 默认只加载当天数据，大幅减少加载时间

**数据采集**：
- 创建 `collect_daily_anchor_data.py` 脚本，从 `anchor_profit_stats.jsonl` 中提取指定日期的数据
- 2026-01-28 数据采集完成：732条记录，5.70 MB（未压缩），392.69 KB（压缩）

**当前数据状态**：
- 最新数据：2026-01-28（732条记录）
- 最后采集时间：2026-01-28 12:20:36
- 数据时间跨度：2025-12-27 至 2026-01-28

### 2. 历史极值记录 - 按日期存储
**数据目录**：`/home/user/webapp/data/extreme_jsonl_daily/`

**文件命名**：`extreme_real_YYYYMMDD.jsonl`

**实现**：
- 创建 `ExtremeDailyJSONLManager` 类，按日期分区存储极值记录
- 每天一个文件，避免单个文件过大
- 使用绝对路径 `/home/user/webapp/data/extreme_jsonl_daily/` 确保路径解析正确

**数据迁移**：
- 原文件 `extreme_real.jsonl` 已损坏，无法读取
- 从当前持仓重新生成今天的极值记录：
  - 文件：`extreme_real_20260128.jsonl`
  - 记录数：44条（多单20条，空单24条）
  - 盈利记录：41条
  - 亏损记录：3条
  - 文件大小：15.02 KB

**示例记录**：
```
BNB-USDT-SWAP long highest_profit: 2637.01%
UNI-USDT-SWAP long highest_profit: 619.27%
NEAR-USDT-SWAP long highest_profit: 419.39%
ETC-USDT-SWAP long highest_profit: 1505.17%
LTC-USDT-SWAP long highest_profit: 2198.91%
```

### 3. API修改

#### `/api/anchor-profit/by-date`
**参数**：
- `date`：日期（YYYY-MM-DD格式），默认今天
- `type`：数据类型，默认 `profit_stats`

**返回**：
```json
{
  "success": true,
  "date": "2026-01-28",
  "data": [...],
  "count": 732,
  "statistics": {
    "total_records": 732,
    "data_types": {"profit_stats": 732}
  }
}
```

#### `/api/anchor-system/profit-records-with-coins`
**参数**：
- `trade_mode`：交易模式（real/paper），默认 real
- `date`：日期（YYYY-MM-DD格式），可选，不指定则加载今天
- `limit`：限制返回记录数，可选

**修改**：
- 使用 `ExtremeDailyJSONLManager` 替代旧的 `ExtremeJSONLManager`
- 支持按日期查询，默认只加载当天数据
- 加载速度大幅提升（从加载全部记录 → 只加载当天记录）

**返回示例**：
```json
{
  "success": true,
  "total": 44,
  "trade_mode": "real",
  "date": "2026-01-28",
  "data_source": "JSONL (filtered by date)",
  "records": [
    {
      "inst_id": "BNB-USDT-SWAP",
      "pos_side": "long",
      "record_type": "highest_profit",
      "profit_rate": 26.3701,
      "timestamp": "2026-01-28 04:25:36"
    }
  ],
  "coins_data": {...}
}
```

### 4. 前端修改

#### 多空单盈利统计图表
- 修改 `loadProfitStatsByDate()` 函数，支持向前查找最近有数据的日期
- 当今天没有数据时，自动回退查找最多30天内的最新数据
- 解决了数据断档时显示"暂无数据"的问题

#### 历史极值记录表
- API调用修改为按日期加载：`/api/anchor-system/profit-records-with-coins?trade_mode=real&date=${date}`
- 前端自动使用今天的日期
- 支持通过日期选择器查看历史日期的数据

### 5. 辅助脚本

#### `collect_daily_anchor_data.py`
**功能**：从 `anchor_profit_stats.jsonl` 中提取指定日期的数据并归档

**使用方法**：
```bash
# 采集今天的数据
python3 collect_daily_anchor_data.py

# 采集指定日期的数据
python3 collect_daily_anchor_data.py 2026-01-27
```

**输出**：
- 未压缩：`data/anchor_daily/anchor_data_YYYY-MM-DD.jsonl`
- 压缩版：`data/anchor_daily/anchor_data_YYYY-MM-DD.jsonl.gz`

#### `generate_today_extreme.py`
**功能**：从当前持仓生成今天的极值记录

**使用场景**：
- 旧的极值记录文件损坏时
- 重新初始化极值记录系统时

**输出**：
- 文件：`data/extreme_jsonl_daily/extreme_real_YYYYMMDD.jsonl`

#### `migrate_extreme_to_daily.py`
**功能**：将旧的 `extreme_real.jsonl` 迁移到按日期分区的存储

**状态**：由于源文件损坏，迁移失败。已通过 `generate_today_extreme.py` 从当前持仓重新生成今天的数据。

## 修改文件清单

### 核心代码
1. `source_code/app_new.py`
   - 添加 `sys.path` 设置确保模块导入正确
   - 修改 `/api/anchor-system/profit-records-with-coins` 使用新的按日期管理器

2. `source_code/extreme_daily_jsonl_manager.py`
   - 创建按日期分区的极值记录管理器
   - 使用绝对路径避免路径解析问题

3. `source_code/templates/anchor_system_real.html`
   - 修改数据加载逻辑，支持按日期查询
   - 添加自动查找最近有数据日期的功能

### 辅助脚本
4. `collect_daily_anchor_data.py` - 每日数据采集脚本
5. `generate_today_extreme.py` - 从持仓生成极值记录
6. `migrate_extreme_to_daily.py` - 数据迁移脚本（因源文件损坏未使用）

## 测试结果

### 多空单盈利统计 API 测试
```bash
# 测试今天的数据
curl "http://localhost:5000/api/anchor-profit/by-date?date=2026-01-28&type=profit_stats"
✅ 成功：732条记录
✅ 最新时间：2026-01-28 04:20:36
```

### 历史极值记录 API 测试
```bash
# 测试今天的极值记录
curl "http://localhost:5000/api/anchor-system/profit-records-with-coins?trade_mode=real&date=2026-01-28"
✅ 成功：44条记录
✅ 数据源：JSONL (filtered by date)
✅ 示例：BNB-USDT-SWAP long highest_profit 2637.01%
```

### 前端页面测试
- ✅ 页面加载速度大幅提升（只加载当天数据）
- ✅ 多空单盈利统计图表正常显示
- ✅ 历史极值记录表正常显示
- ✅ 日期选择器功能正常

## 性能提升

### 多空单盈利统计
- **修改前**：加载全部 11,613 条记录
- **修改后**：只加载当天 732 条记录
- **性能提升**：加载数据量减少 94%

### 历史极值记录
- **修改前**：尝试加载损坏的 214 KB 文件（失败）
- **修改后**：只加载今天的 15 KB 文件（44条记录）
- **性能提升**：加载速度大幅提升，数据可靠性增强

## 数据存储优化

### 文件大小对比
**多空单盈利统计**（以 2026-01-28 为例）：
- 未压缩：5.70 MB
- 压缩后：392.69 KB
- 压缩率：93.1%

**历史极值记录**（2026-01-28）：
- 文件大小：15.02 KB
- 记录数：44条

### 存储结构
```
data/
├── anchor_daily/              # 多空单盈利统计（按日期）
│   ├── anchor_data_2026-01-28.jsonl      (5.70 MB)
│   └── anchor_data_2026-01-28.jsonl.gz   (392.69 KB)
└── extreme_jsonl_daily/       # 历史极值记录（按日期）
    └── extreme_real_20260128.jsonl       (15.02 KB)
```

## 访问地址
https://5000-ikmpd2up5chrwx4jjjkih-5634da27.sandbox.novita.ai/anchor-system-real

## Git 提交
```
Commit: ec9d444
Message: fix: 历史极值记录改为按日期存储，每天一个JSONL文件

- 创建 ExtremeDailyJSONLManager，按日期分区存储极值记录
- 修改 API 使用新的按日期管理器，只加载当天数据
- 使用绝对路径确保路径解析正确
- 从当前持仓生成今天的极值记录（44条）
- 数据文件：data/extreme_jsonl_daily/extreme_real_YYYYMMDD.jsonl
- 修复前端日期选择器，支持查看历史日期数据

Files changed: 4
Insertions: 282
Deletions: 121
```

## 后续建议

1. **定时采集任务**
   - 建议每天凌晨2点自动运行 `collect_daily_anchor_data.py`
   - 可使用 crontab 或 PM2 定时任务

2. **数据备份**
   - 定期备份 `data/anchor_daily/` 目录
   - 定期备份 `data/extreme_jsonl_daily/` 目录

3. **历史数据迁移**
   - 如果找到可用的备份，运行 `migrate_extreme_to_daily.py` 迁移历史数据
   - 当前只有今天的极值记录，历史数据需要补充

4. **监控告警**
   - 监控数据采集是否正常运行
   - 检测数据断档情况（如 2026-01-24 至 2026-01-27 无数据）

## 状态
✅ **已完成** - 2026-01-28

所有核心功能已实现并测试通过：
- ✅ 按日期存储多空单盈利统计数据
- ✅ 按日期存储历史极值记录
- ✅ API 支持按日期查询
- ✅ 前端只加载当天数据，大幅提升加载速度
- ✅ 创建数据采集和生成脚本
- ✅ 代码已提交到 git

## 联系方式
如有问题，请联系开发团队。
