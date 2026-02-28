# 27币追踪系统 - 重新部署数据迁移完整流程

**文档版本**: v1.0  
**更新日期**: 2026-02-24  
**系统URL**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai

---

## 📋 目录

1. [系统概述](#系统概述)
2. [数据结构说明](#数据结构说明)
3. [迁移前准备](#迁移前准备)
4. [数据导出流程](#数据导出流程)
5. [数据导入流程](#数据导入流程)
6. [服务启动与验证](#服务启动与验证)
7. [常见问题处理](#常见问题处理)
8. [完整自动化脚本](#完整自动化脚本)

---

## 系统概述

### 核心功能
- **27币种实时追踪**: BTC、ETH、BNB、XRP、DOGE、SOL、DOT、MATIC、LTC、LINK等
- **数据采集**: 每分钟采集一次价格和涨跌幅
- **波峰检测**: 自动识别B点(低点)、A点(反弹高点)、C点(回落点)
- **暴跌预警**: 基于波峰模式的8种预警情况检测
- **RSI指标**: 14周期RSI计算与追踪

### 数据收集器
- **主进程**: `coin-change-tracker` (PM2管理)
- **脚本路径**: `/home/user/webapp/source_code/coin_change_tracker_collector.py`
- **数据目录**: `/home/user/webapp/data/coin_change_tracker/`
- **总数据量**: 约112MB (35个JSONL文件)

---

## 数据结构说明

### 1. 币种涨跌数据 (coin_change_YYYYMMDD.jsonl)

**文件命名**: `coin_change_20260224.jsonl`  
**文件大小**: 每天约2-4MB  
**数据格式**:
```json
{
  "timestamp": "2026-02-24T13:06:00.123456+08:00",
  "BTC": -1.23,
  "ETH": 0.45,
  "BNB": -0.12,
  ... (27个币种)
}
```

**关键字段说明**:
- `timestamp`: ISO 8601格式，北京时间(+08:00)
- 币种字段: 当前涨跌幅百分比(相对于基线价格)

**每日记录数**: 约1440条 (每分钟1条 × 24小时)

### 2. RSI指标数据 (rsi_YYYYMMDD.jsonl)

**文件命名**: `rsi_20260224.jsonl`  
**文件大小**: 每天约100-130KB  
**数据格式**:
```json
{
  "timestamp": "2026-02-24T13:06:00.123456+08:00",
  "BTC_rsi": 65.4,
  "ETH_rsi": 52.3,
  "BNB_rsi": 48.9,
  ... (27个币种_rsi)
}
```

### 3. 基线价格 (baseline_YYYYMMDD.json)

**文件命名**: `baseline_20260224.json`  
**文件大小**: 约1KB  
**数据格式**:
```json
{
  "date": "20260224",
  "timestamp": "2026-02-24T02:00:00+08:00",
  "BTC": 98765.43,
  "ETH": 3456.78,
  ... (27个币种基线价格)
}
```

**更新时间**: 每天北京时间02:00自动更新

### 4. 暴跌预警数据 (crash_warning_events/)

**目录**: `/home/user/webapp/data/crash_warning_events/`  
**文件类型**:
- `february_analysis.json`: 月度分析汇总
- 日度预警记录 (按需生成)

---

## 迁移前准备

### 1. 环境检查

```bash
# 切换到项目目录
cd /home/user/webapp

# 检查当前运行的服务
pm2 list

# 确认数据目录
ls -lh data/coin_change_tracker/

# 检查磁盘空间 (至少需要200MB)
df -h /home/user/webapp
```

### 2. 停止数据采集 (旧系统)

```bash
cd /home/user/webapp

# 停止币种追踪采集器
pm2 stop coin-change-tracker

# 确认已停止
pm2 list | grep coin-change-tracker
```

**⚠️ 重要**: 必须停止采集器，否则导出过程中数据可能不一致

### 3. 确认需要迁移的数据

```bash
cd /home/user/webapp

# 统计JSONL文件数量
ls -1 data/coin_change_tracker/*.jsonl | wc -l

# 查看数据时间范围
ls -1 data/coin_change_tracker/coin_change_*.jsonl | head -5
ls -1 data/coin_change_tracker/coin_change_*.jsonl | tail -5

# 查看总数据量
du -sh data/coin_change_tracker/
```

**预期结果**:
- JSONL文件: 35个左右
- 数据时间范围: 2026-01-22 至 2026-02-24
- 总大小: 约112MB

---

## 数据导出流程

### 方案A: 使用数据同步工具 (推荐)

我们已经有完整的数据同步系统，参考 `DATA_SYNC_GUIDE.md`

#### 步骤1: 导出当前系统数据

```bash
cd /home/user/webapp

# 导出所有数据
node scripts/export_daily_data.js http://localhost:9002 data_backup_$(date +%Y%m%d).json

# 查看导出结果
ls -lh data_backup_*.json
```

**导出内容包括**:
- `coin_change_YYYYMMDD.jsonl` (所有日期)
- `rsi_YYYYMMDD.jsonl` (所有日期)
- `baseline_YYYYMMDD.json` (所有日期)
- 波峰记录
- 暴跌预警记录
- 日度预测数据

#### 步骤2: 验证导出文件

```bash
cd /home/user/webapp

# 检查导出文件
jq '.files | length' data_backup_*.json
jq '.metadata' data_backup_*.json

# 查看文件大小
ls -lh data_backup_*.json
```

**预期输出**:
```json
{
  "files": 70,
  "total_size": "112MB",
  "export_date": "2026-02-24T13:30:00+08:00"
}
```

### 方案B: 手动打包 (备选方案)

适用于数据同步工具不可用的情况

```bash
cd /home/user/webapp

# 创建备份目录
mkdir -p backups/$(date +%Y%m%d)

# 打包所有数据
tar -czf backups/$(date +%Y%m%d)/coin_change_data_$(date +%Y%m%d_%H%M%S).tar.gz \
  data/coin_change_tracker/*.jsonl \
  data/coin_change_tracker/baseline_*.json \
  data/crash_warning_events/ \
  2>/dev/null

# 验证打包文件
tar -tzf backups/$(date +%Y%m%d)/coin_change_data_*.tar.gz | head -20

# 查看文件大小
ls -lh backups/$(date +%Y%m%d)/
```

---

## 数据导入流程

### 在新系统上执行

### 步骤1: 准备新环境

```bash
# 切换到项目目录
cd /home/user/webapp

# 确保数据目录存在
mkdir -p data/coin_change_tracker
mkdir -p data/crash_warning_events

# 确认PM2已安装
pm2 --version

# 确认Python环境
python3 --version
pip3 list | grep -E "requests|numpy|pytz"
```

### 步骤2: 导入数据

#### 使用数据同步工具导入

```bash
cd /home/user/webapp

# 从旧系统导入
node scripts/import_daily_data.js http://localhost:9002 data_backup_20260224.json

# 查看导入日志
tail -f /tmp/import_*.log
```

**导入过程**:
1. 自动创建必要目录
2. 备份现有文件 (如果有)
3. 批量写入新文件
4. 验证文件完整性
5. 显示导入统计

#### 手动解压导入

```bash
cd /home/user/webapp

# 解压备份文件
tar -xzf coin_change_data_20260224_*.tar.gz -C /tmp/

# 移动到数据目录
mv /tmp/data/coin_change_tracker/*.jsonl data/coin_change_tracker/
mv /tmp/data/coin_change_tracker/baseline_*.json data/coin_change_tracker/
mv /tmp/data/crash_warning_events/* data/crash_warning_events/

# 设置权限
chmod 644 data/coin_change_tracker/*
chmod 755 data/coin_change_tracker
chmod 755 data/crash_warning_events
```

### 步骤3: 验证数据完整性

```bash
cd /home/user/webapp

# 统计文件数量
echo "JSONL文件数: $(ls -1 data/coin_change_tracker/*.jsonl 2>/dev/null | wc -l)"
echo "基线文件数: $(ls -1 data/coin_change_tracker/baseline_*.json 2>/dev/null | wc -l)"

# 验证最新数据日期
ls -lt data/coin_change_tracker/coin_change_*.jsonl | head -3

# 检查文件大小分布
ls -lh data/coin_change_tracker/coin_change_*.jsonl | tail -10

# 验证数据格式
head -1 data/coin_change_tracker/coin_change_20260224.jsonl | jq '.'
```

**预期输出**:
```
JSONL文件数: 35
基线文件数: 33
```

---

## 服务启动与验证

### 步骤1: 启动币种追踪采集器

```bash
cd /home/user/webapp

# 使用PM2启动
pm2 start source_code/coin_change_tracker_collector.py \
  --name coin-change-tracker \
  --interpreter python3 \
  --cron-restart="0 2 * * *" \
  --log-date-format="YYYY-MM-DD HH:mm:ss"

# 查看状态
pm2 list | grep coin-change-tracker

# 查看日志
pm2 logs coin-change-tracker --lines 50 --nostream
```

**预期日志输出**:
```
[2026-02-24 13:30:00] 币种追踪采集器启动
[2026-02-24 13:30:05] 已加载基线价格: 2026-02-24
[2026-02-24 13:31:00] ✓ 数据采集成功 - 27个币种
[2026-02-24 13:31:00] 写入: coin_change_20260224.jsonl
```

### 步骤2: 启动Web服务

```bash
cd /home/user/webapp

# 重启Flask应用
pm2 restart flask-app

# 查看状态
pm2 list | grep flask-app

# 查看启动日志
pm2 logs flask-app --lines 30 --nostream
```

### 步骤3: 验证Web界面

访问系统URL: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai

**验证检查项**:
1. **币种追踪页面**: `/coin-change-tracker`
   - [ ] 显示27个币种实时涨跌
   - [ ] RSI之和曲线正常显示 (灰色粗线)
   - [ ] 波峰标记正确 (B点绿色, A点橙色, C点灰色)
   
2. **暴跌预警卡片**:
   - [ ] 显示当天预警状态
   - [ ] 折叠/展开功能正常
   - [ ] 预警历史记录正确

3. **数据更新**:
   - [ ] 等待1-2分钟，刷新页面
   - [ ] 确认时间戳更新
   - [ ] 确认涨跌幅数据变化

### 步骤4: 健康检查

```bash
cd /home/user/webapp

# 检查最新数据文件
ls -lt data/coin_change_tracker/*.jsonl | head -3

# 验证数据正在写入
tail -f data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 检查文件行数 (应该逐渐增加)
wc -l data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl
sleep 60
wc -l data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl
```

---

## 常见问题处理

### 问题1: 数据采集器无法启动

**症状**: PM2显示 `errored` 或 `stopped`

**排查步骤**:
```bash
# 查看错误日志
pm2 logs coin-change-tracker --err --lines 50

# 常见错误原因:
# 1. Python依赖缺失
pip3 install requests numpy pytz

# 2. 数据目录不存在
mkdir -p /home/user/webapp/data/coin_change_tracker

# 3. 权限问题
chmod 755 /home/user/webapp/data/coin_change_tracker

# 重新启动
pm2 delete coin-change-tracker
pm2 start source_code/coin_change_tracker_collector.py --name coin-change-tracker --interpreter python3
```

### 问题2: 数据文件未更新

**症状**: JSONL文件时间戳不是最新的

**排查步骤**:
```bash
# 1. 确认进程正在运行
pm2 list | grep coin-change-tracker

# 2. 查看实时日志
pm2 logs coin-change-tracker --lines 0

# 3. 手动测试采集
python3 source_code/coin_change_tracker_collector.py

# 4. 检查网络连接
curl -I https://api.binance.com/api/v3/ticker/24hr
```

### 问题3: RSI之和曲线不显示

**症状**: Web页面上RSI曲线消失或显示为细线

**解决方案**:
```bash
# 1. 检查RSI数据文件
ls -lh data/coin_change_tracker/rsi_$(date +%Y%m%d).jsonl

# 2. 验证RSI数据格式
head -1 data/coin_change_tracker/rsi_$(date +%Y%m%d).jsonl | jq '.'

# 3. 查看前端代码 (已在PR #1中修复)
grep -A 10 "name: 'RSI之和'" templates/coin_change_tracker.html

# 4. 清除浏览器缓存，强制刷新 (Ctrl+Shift+R)
```

**参考**: PR https://github.com/jamesyidc/1212335551/pull/1 (Commit bf99b2b)

### 问题4: 暴跌预警未触发

**症状**: 明显应该预警的情况未被检测

**排查步骤**:
```bash
# 1. 运行2月份完整分析
cd /home/user/webapp
python3 scripts/check_february_crash_warnings.py

# 2. 查看分析结果
cat data/crash_warning_events/february_analysis.json | jq '.'

# 3. 检查波峰检测逻辑
grep -A 20 "def detect_crash_warning" source_code/wave_peak_detector.py

# 4. 手动调试特定日期
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/user/webapp/source_code')
from wave_peak_detector import WavePeakDetector

detector = WavePeakDetector()
data = detector.load_data('20260206')
peaks, state = detector.detect_wave_peaks(data)
print(f"检测到 {len(peaks)} 个波峰")
EOF
```

### 问题5: 磁盘空间不足

**症状**: 数据写入失败，PM2日志显示 `No space left on device`

**解决方案**:
```bash
# 1. 检查磁盘使用
df -h /home/user/webapp

# 2. 清理旧数据 (保留最近30天)
cd /home/user/webapp
find data/coin_change_tracker -name "coin_change_*.jsonl" -mtime +30 -delete
find data/coin_change_tracker -name "rsi_*.jsonl" -mtime +30 -delete

# 3. 压缩历史数据
cd data/coin_change_tracker
tar -czf archive_$(date +%Y%m).tar.gz coin_change_202601*.jsonl
rm -f coin_change_202601*.jsonl

# 4. 移动归档到其他位置
mv archive_*.tar.gz /mnt/aidrive/backups/
```

---

## 完整自动化脚本

### 一键迁移脚本: `migrate_coin_tracker.sh`

```bash
#!/bin/bash
# 27币追踪系统数据迁移自动化脚本
# 用法: bash migrate_coin_tracker.sh [export|import]

set -e  # 遇到错误立即退出

WEBAPP_DIR="/home/user/webapp"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="coin_tracker_backup_${BACKUP_DATE}.json"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 导出函数
do_export() {
    log_info "开始导出币种追踪数据..."
    
    cd "$WEBAPP_DIR"
    
    # 1. 停止采集器
    log_info "停止数据采集器..."
    pm2 stop coin-change-tracker || log_warn "采集器未运行"
    sleep 2
    
    # 2. 导出数据
    log_info "使用数据同步工具导出..."
    node scripts/export_daily_data.js http://localhost:9002 "$BACKUP_FILE"
    
    # 3. 验证导出
    if [ -f "$BACKUP_FILE" ]; then
        FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        FILE_COUNT=$(jq '.files | length' "$BACKUP_FILE")
        log_info "✓ 导出完成: $BACKUP_FILE"
        log_info "  文件大小: $FILE_SIZE"
        log_info "  文件数量: $FILE_COUNT"
    else
        log_error "导出失败: 未找到备份文件"
        exit 1
    fi
    
    # 4. 重启采集器
    log_info "重启数据采集器..."
    pm2 start coin-change-tracker
    
    log_info "导出流程完成! 备份文件: $BACKUP_FILE"
}

# 导入函数
do_import() {
    if [ -z "$2" ]; then
        log_error "请指定备份文件: $0 import <backup_file.json>"
        exit 1
    fi
    
    IMPORT_FILE="$2"
    
    if [ ! -f "$IMPORT_FILE" ]; then
        log_error "备份文件不存在: $IMPORT_FILE"
        exit 1
    fi
    
    log_info "开始导入币种追踪数据..."
    
    cd "$WEBAPP_DIR"
    
    # 1. 创建必要目录
    log_info "创建数据目录..."
    mkdir -p data/coin_change_tracker
    mkdir -p data/crash_warning_events
    
    # 2. 备份现有数据
    if [ -d "data/coin_change_tracker" ] && [ "$(ls -A data/coin_change_tracker)" ]; then
        log_warn "检测到现有数据，创建备份..."
        EXISTING_BACKUP="data_backup_existing_${BACKUP_DATE}.tar.gz"
        tar -czf "$EXISTING_BACKUP" data/coin_change_tracker/ data/crash_warning_events/ 2>/dev/null || true
        log_info "  现有数据备份至: $EXISTING_BACKUP"
    fi
    
    # 3. 导入数据
    log_info "使用数据同步工具导入..."
    node scripts/import_daily_data.js http://localhost:9002 "$IMPORT_FILE"
    
    # 4. 验证导入
    JSONL_COUNT=$(ls -1 data/coin_change_tracker/*.jsonl 2>/dev/null | wc -l)
    BASELINE_COUNT=$(ls -1 data/coin_change_tracker/baseline_*.json 2>/dev/null | wc -l)
    
    log_info "✓ 导入完成!"
    log_info "  JSONL文件数: $JSONL_COUNT"
    log_info "  基线文件数: $BASELINE_COUNT"
    
    # 5. 启动服务
    log_info "启动币种追踪采集器..."
    pm2 delete coin-change-tracker 2>/dev/null || true
    pm2 start source_code/coin_change_tracker_collector.py \
        --name coin-change-tracker \
        --interpreter python3 \
        --cron-restart="0 2 * * *"
    
    sleep 3
    
    # 6. 重启Web服务
    log_info "重启Flask应用..."
    pm2 restart flask-app
    
    sleep 2
    
    # 7. 健康检查
    log_info "执行健康检查..."
    pm2 list | grep -E "coin-change-tracker|flask-app"
    
    log_info "导入流程完成!"
    log_info "请访问: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker"
}

# 主逻辑
case "$1" in
    export)
        do_export
        ;;
    import)
        do_import "$@"
        ;;
    *)
        echo "用法: $0 {export|import <backup_file.json>}"
        echo ""
        echo "示例:"
        echo "  导出: $0 export"
        echo "  导入: $0 import coin_tracker_backup_20260224_133000.json"
        exit 1
        ;;
esac
```

### 使用自动化脚本

```bash
# 保存脚本
cat > /home/user/webapp/migrate_coin_tracker.sh << 'SCRIPT_END'
# [粘贴上面的完整脚本内容]
SCRIPT_END

# 添加执行权限
chmod +x /home/user/webapp/migrate_coin_tracker.sh

# 导出数据 (在旧系统上)
cd /home/user/webapp
./migrate_coin_tracker.sh export

# 导入数据 (在新系统上)
cd /home/user/webapp
./migrate_coin_tracker.sh import coin_tracker_backup_20260224_133000.json
```

---

## 快速参考命令

### 日常运维

```bash
# 查看服务状态
pm2 list | grep coin

# 查看实时日志
pm2 logs coin-change-tracker --lines 0

# 重启采集器
pm2 restart coin-change-tracker

# 查看最新数据
tail -5 data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl | jq '.'

# 统计今日数据量
wc -l data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl
```

### 数据分析

```bash
# 运行2月份暴跌预警分析
python3 scripts/check_february_crash_warnings.py

# 查看分析结果
cat data/crash_warning_events/february_analysis.json | jq '.'

# 查看特定日期波峰
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/user/webapp/source_code')
from wave_peak_detector import WavePeakDetector
detector = WavePeakDetector()
data = detector.load_data('20260206')
peaks, state = detector.detect_wave_peaks(data)
for i, peak in enumerate(peaks, 1):
    print(f"波峰{i}: B={peak['b_point']['value']:.2f}% A={peak['a_point']['value']:.2f}% 幅度={peak['amplitude']:.2f}%")
EOF
```

### 数据备份

```bash
# 每日自动备份 (添加到crontab)
0 3 * * * cd /home/user/webapp && ./migrate_coin_tracker.sh export && mv coin_tracker_backup_*.json /mnt/aidrive/backups/

# 手动备份
cd /home/user/webapp
./migrate_coin_tracker.sh export
```

---

## 相关文档

- **数据同步指南**: `DATA_SYNC_GUIDE.md`
- **快速参考**: `DATA_SYNC_QUICK_REF.md`
- **开发报告**: `DATA_SYNC_DEVELOPMENT_REPORT.md`
- **系统架构**: `SYSTEM_ARCHITECTURE.md`
- **API文档**: `API_DOCUMENTATION.md`

---

## 技术支持

### 系统信息
- **项目仓库**: https://github.com/jamesyidc/1212335551
- **当前PR**: https://github.com/jamesyidc/1212335551/pull/1
- **系统URL**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai

### 关键修复
- **RSI曲线显示**: PR #1, Commit bf99b2b
- **暴跌预警检测**: PR #1, Commit b74fb45

### 联系方式
如有问题，请在GitHub仓库中提Issue或联系开发团队。

---

**最后更新**: 2026-02-24  
**文档状态**: ✅ 生产就绪
