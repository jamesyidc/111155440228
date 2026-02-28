# 数据补齐指南 - 重新部署后的数据恢复

## 🎯 使用场景

当您重新部署27币追踪系统时，通常需要1-2小时的时间：
- **备份数据**: 10-20分钟
- **传输文件**: 20-40分钟  
- **部署系统**: 10-20分钟
- **启动服务**: 5-10分钟

**问题**: 这段时间内，数据采集器停止运行，导致数据缺失。

**解决方案**: 使用数据补齐工具，从OKX历史K线API获取缺失时段的数据。

---

## 🚀 快速开始 (3步完成)

### 步骤1: 重新部署完成后，立即执行

```bash
cd /home/user/webapp
./quick_backfill.sh --last-2h
```

### 步骤2: 等待补齐完成

脚本会自动:
- ✅ 检查环境和依赖
- ✅ 获取最近2小时的K线数据
- ✅ 计算涨跌幅和RSI指标
- ✅ 写入JSONL文件

### 步骤3: 验证数据

```bash
# 查看今日数据文件
ls -lh data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 查看最新记录
tail -5 data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 访问Web界面验证
# https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
```

---

## 📖 详细使用说明

### 一、快速补齐模式 (推荐)

#### 补齐最近2小时 (最常用)

```bash
cd /home/user/webapp
./quick_backfill.sh --last-2h
```

**适用场景**: 标准部署流程（1.5-2小时）

#### 补齐最近1小时

```bash
cd /home/user/webapp
./quick_backfill.sh --last-1h
```

**适用场景**: 快速重启或短暂停机

### 二、自定义时间范围

#### 指定具体时间段

```bash
cd /home/user/webapp
./quick_backfill.sh --custom 13:00 15:30
```

**说明**:
- 第一个时间: 开始时间 (HH:MM)
- 第二个时间: 结束时间 (HH:MM)
- 时间范围: 必须在当天内

**示例场景**:
```bash
# 备份开始: 2026-02-24 13:00
# 部署完成: 2026-02-24 15:30
# 补齐命令:
./quick_backfill.sh --custom 13:00 15:30
```

### 三、交互式模式

```bash
cd /home/user/webapp
./quick_backfill.sh
```

**交互流程**:
1. 显示当前时间和默认范围
2. 输入开始时间 (或回车使用默认)
3. 输入结束时间 (或回车使用默认)
4. 确认后开始补齐

**示例输出**:
```
当前北京时间: 2026-02-24 15:30:00
目标日期: 20260224

请输入需要补齐的时间范围:
开始时间 (格式: HH:MM, 默认 13:30): 13:00
结束时间 (格式: HH:MM, 默认 15:30): 

开始补齐...
```

---

## 🔍 工作原理

### 数据来源

脚本从 **OKX历史K线API** 获取数据:
- API: `https://www.okx.com/api/v5/market/history-candles`
- 频率: 1分钟K线
- 币种: 27个主流币种
- 限制: 最多300根K线 (5小时)

### 补齐流程

```
1. 加载基线价格 (baseline_YYYYMMDD.json)
   ↓
2. 检查已有数据时间戳
   ↓
3. 获取27个币种的K线数据 (每个币种1-2秒)
   ↓
4. 计算涨跌幅 = (收盘价 - 基线价) / 基线价 × 100%
   ↓
5. 计算RSI指标 (14周期)
   ↓
6. 写入JSONL文件 (只补齐缺失的时间点)
   ↓
7. 完成
```

### 数据格式

#### 涨跌幅数据 (coin_change_YYYYMMDD.jsonl)

```json
{
  "timestamp": "2026-02-24T13:30:00",
  "BTC": -1.23,
  "ETH": 0.45,
  "BNB": -0.12,
  ... (27个币种)
}
```

#### RSI指标数据 (rsi_YYYYMMDD.jsonl)

```json
{
  "timestamp": "2026-02-24T13:30:00",
  "BTC_rsi": 65.4,
  "ETH_rsi": 52.3,
  ... (27个币种_rsi)
}
```

---

## 📊 实际案例

### 案例1: 标准部署流程

**时间线**:
```
14:00 - 旧系统停止采集器
14:05 - 开始备份数据
14:25 - 备份完成，开始传输
14:50 - 传输完成，开始部署
15:10 - 部署完成，启动服务
15:15 - 服务正常运行
```

**数据缺失**: 14:00 - 15:15 (1小时15分钟)

**补齐命令**:
```bash
# 方式1: 快速模式 (补齐最近2小时，包含缺失时段)
./quick_backfill.sh --last-2h

# 方式2: 精确模式 (只补齐缺失时段)
./quick_backfill.sh --custom 14:00 15:15
```

**执行结果**:
```
📊 步骤1: 加载基线价格...
  ✅ 基线价格已加载 (27 个币种)

📊 步骤2: 检查已有数据...
  ℹ️  已有 840 条记录

📊 步骤3: 获取 27 个币种的K线数据...
  [ 1/27] BTC      ✅ 75 根K线
  [ 2/27] ETH      ✅ 75 根K线
  ...
  ✅ 成功获取 27/27 个币种的数据

📊 步骤4: 构建时间序列数据...
  ℹ️  共找到 75 个时间点
  ℹ️  需要补齐 75 个时间点

📊 步骤5: 写入补齐数据...
  ✓ 已补齐 10/75 条记录
  ✓ 已补齐 20/75 条记录
  ...
  ✓ 已补齐 75/75 条记录

✅ 补齐完成!
  新增记录: 75 条
```

### 案例2: 快速重启

**时间线**:
```
16:30 - 系统维护，停止服务
16:45 - 维护完成，重启服务
```

**数据缺失**: 16:30 - 16:45 (15分钟)

**补齐命令**:
```bash
./quick_backfill.sh --last-1h
```

---

## ⚠️ 注意事项

### 前提条件

1. **基线文件必须存在**
   ```bash
   # 检查基线文件
   ls -lh data/coin_change_tracker/baseline_$(date +%Y%m%d).json
   ```
   
   如果不存在:
   - 等待每天北京时间02:00自动生成
   - 或手动创建基线文件

2. **Python环境正常**
   ```bash
   # 检查Python版本
   python3 --version
   
   # 检查依赖包
   pip3 list | grep -E "requests|numpy|pytz"
   ```
   
   如果依赖缺失:
   ```bash
   pip3 install requests numpy pytz
   ```

3. **数据目录存在**
   ```bash
   # 检查目录
   ls -ld data/coin_change_tracker/
   ```

### 限制说明

1. **时间范围限制**
   - 最大补齐范围: 5小时 (API限制)
   - 只能补齐当天数据
   - 不能补齐历史日期的数据

2. **数据精度**
   - 使用1分钟K线的收盘价
   - RSI基于5分钟K线计算
   - 与实时采集可能有细微差异 (±0.1%)

3. **API限流**
   - 每个币种间隔0.5秒请求
   - 27个币种总耗时约15-20秒
   - 避免频繁执行

### 常见错误

#### 错误1: 基线文件不存在

```
❌ 未找到基线价格文件: baseline_20260224.json
```

**解决方案**:
- 检查日期是否正确
- 确认采集器是否在02:00正常运行
- 或从旧系统复制基线文件

#### 错误2: Python依赖缺失

```
ModuleNotFoundError: No module named 'requests'
```

**解决方案**:
```bash
pip3 install requests numpy pytz
```

#### 错误3: K线获取失败

```
⚠️  BTC K线获取失败
```

**可能原因**:
- 网络问题
- API限流
- 币种符号错误

**解决方案**:
- 等待几分钟后重试
- 检查网络连接
- 查看脚本日志

---

## 🔧 高级用法

### 仅补齐特定币种

编辑 `scripts/backfill_today_data.py`:
```python
# 原代码
SYMBOLS = [
    'BTC', 'ETH', 'BNB', ...
]

# 修改为只补齐BTC和ETH
SYMBOLS = ['BTC', 'ETH']
```

### 自定义K线来源

默认使用OKX API，可修改为其他交易所:
```python
# Binance API
url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1m&limit=300"

# Huobi API
url = f"https://api.huobi.pro/market/history/kline?symbol={symbol.lower()}usdt&period=1min&size=300"
```

### 批量补齐多天

如果需要补齐多天的数据，可循环执行:
```bash
#!/bin/bash
# 补齐最近3天的数据

for i in {0..2}; do
    DATE=$(date -d "$i days ago" +%Y%m%d)
    echo "补齐 $DATE 的数据..."
    
    # 修改脚本支持指定日期
    python3 scripts/backfill_today_data.py --date $DATE --auto
done
```

---

## 📈 验证数据完整性

### 检查文件行数

```bash
# 查看今日数据行数
wc -l data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 理论记录数 = 已运行分钟数
# 例如: 从02:00到16:00 = 14小时 = 840分钟 = 840条记录
```

### 检查时间戳连续性

```bash
# 提取所有时间戳
grep -oP '"timestamp":"[^"]+' data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl | \
    cut -d'"' -f4 | \
    sort | \
    uniq -c

# 如果某分钟有多条记录，说明重复
# 如果某分钟缺失，说明有数据缺口
```

### Web界面验证

访问: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker

检查项:
- [ ] 图表曲线是否平滑连续
- [ ] 波峰标记是否正确
- [ ] RSI之和曲线是否正常
- [ ] 暴跌预警是否触发

---

## 🎯 最佳实践

### 部署流程建议

```bash
# 1. 停止旧系统采集器
pm2 stop coin-change-tracker

# 2. 记录停止时间
STOP_TIME=$(date '+%H:%M')
echo "停止时间: $STOP_TIME"

# 3. 执行备份和部署
./migrate_coin_tracker.sh export
# ... 传输和部署 ...
./migrate_coin_tracker.sh import backup.json

# 4. 启动新系统
pm2 start coin-change-tracker

# 5. 立即补齐数据
./quick_backfill.sh --last-2h

# 6. 验证数据
pm2 logs coin-change-tracker --lines 20
tail -10 data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl
```

### 自动化脚本

创建 `deploy_with_backfill.sh`:
```bash
#!/bin/bash
# 完整的部署+数据补齐自动化脚本

set -e

echo "开始部署流程..."

# 1. 导出数据
./migrate_coin_tracker.sh export

# 2. 等待用户确认传输完成
read -p "数据已导出，传输完成后按回车继续..." 

# 3. 导入数据
BACKUP_FILE=$(ls -t coin_tracker_backup_*.json | head -1)
./migrate_coin_tracker.sh import "$BACKUP_FILE"

# 4. 补齐数据
./quick_backfill.sh --last-2h

echo "部署完成！"
```

---

## 📞 技术支持

### 相关文档
- `DEPLOYMENT_DATA_MIGRATION_GUIDE.md` - 完整迁移指南
- `DEPLOYMENT_QUICK_REF.md` - 快速参考
- `DEPLOYMENT_SUMMARY.md` - 流程总结

### 相关脚本
- `migrate_coin_tracker.sh` - 数据迁移主脚本
- `quick_backfill.sh` - 数据补齐快捷脚本
- `scripts/backfill_today_data.py` - 数据补齐核心逻辑

### 系统链接
- **Web界面**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker
- **GitHub**: https://github.com/jamesyidc/1212335551
- **PR #1**: https://github.com/jamesyidc/1212335551/pull/1

---

**版本**: v1.0  
**更新**: 2026-02-24  
**状态**: ✅ 生产就绪
