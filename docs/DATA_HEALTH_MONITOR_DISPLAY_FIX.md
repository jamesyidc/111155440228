# 数据健康监控显示修复报告

## 修复时间
2026-02-01 17:00:00

## 问题描述

用户报告数据采集健康监控页面**只显示6个服务**，但实际应该有**8个监控服务**。

### 缺少的服务
- SAR斜率系统
- Google Drive监控

### 统计显示
页面顶部统计卡片显示：
- 监控服务总数：8 ✅ 正确
- 健康服务：6
- 异常服务：2
- 今日自动重启次数：4

但下方只显示了6个服务卡片。

## 根因分析

### API硬编码配置

**文件**：`source_code/app_new.py`
**位置**：`/api/data-health-monitor/status` 端点

```python
# 原代码 ❌
monitor_configs = {
    '27币涨跌幅追踪': 'coin-change-tracker',
    '1小时爆仓金额': 'liquidation-1h-collector',
    '恐慌清洗指数': 'panic-collector',
    '锚点盈利统计': 'anchor-profit-monitor',
    '逃顶信号统计': 'escape-signal-calculator',
    '支撑压力线系统': 'support-resistance-collector'
}
# 只有6个！缺少SAR斜率系统和Google Drive监控
```

### 问题链条

1. **状态文件正确**：`data/data_health_monitor_state.json` 包含8个服务
2. **监控进程正常**：`data_health_monitor.py` 正在监控8个服务
3. **API硬编码**：API端点只返回硬编码的6个服务
4. **页面显示错误**：页面只能显示API返回的6个服务

## 服务状态分析

### 健康的6个服务
1. 27币涨跌幅追踪 - ✅ 健康（延迟0.6分钟）
2. 1小时爆仓金额 - ✅ 健康（延迟0.6分钟）
3. 恐慌清洗指数 - ✅ 健康（延迟0.6分钟）
4. 锚点盈利统计 - ✅ 健康（延迟0.7分钟）
5. 逃顶信号统计 - ✅ 健康（延迟0.2分钟）
6. 支撑压力线系统 - ✅ 健康（仅检查PM2状态）

### 异常的2个服务
7. **SAR斜率系统** - ❌ 异常
   - 状态：unhealthy
   - 数据延迟：153.7分钟
   - PM2状态：online (PID 776693)
   - 连续失败：1次
   - 阈值：10分钟
   - 原因：数据采集中断

8. **Google Drive监控** - ❌ 异常
   - 状态：unhealthy
   - 数据延迟：28.7分钟
   - PM2状态：online (PID 776736)
   - 连续失败：1次
   - 阈值：15分钟
   - 原因：Google Drive TXT文件未更新

## 修复方案

### 1. 添加缺失的监控服务

**文件**：`source_code/app_new.py`
**修改**：在 `monitor_configs` 中添加SAR和Google Drive

```python
# 修改后 ✅
monitor_configs = {
    '27币涨跌幅追踪': 'coin-change-tracker',
    '1小时爆仓金额': 'liquidation-1h-collector',
    '恐慌清洗指数': 'panic-collector',
    '锚点盈利统计': 'anchor-profit-monitor',
    '逃顶信号统计': 'escape-signal-calculator',
    '支撑压力线系统': 'support-resistance-collector',
    'SAR斜率系统': 'sar-jsonl-collector',        # ✅ 新增
    'Google Drive监控': 'gdrive-detector'         # ✅ 新增
}
```

### 2. 未来优化建议

为避免再次出现硬编码不同步的问题，建议：

```python
# 建议：从状态文件动态读取，而不是硬编码
for name, monitor_state in state_data.items():
    monitors.append({
        'name': name,
        'pm2_name': monitor_state.get('pm2_name', ''),  # 需要在状态中保存pm2_name
        'status': monitor_state.get('status', 'unknown'),
        # ...
    })
```

## 验证结果

### 1. API测试 ✅

```bash
$ curl -s "http://localhost:5000/api/data-health-monitor/status" | jq
{
  "stats": {
    "total": 8,           ✅ 8个服务
    "healthy": 6,         ✅ 6个健康
    "unhealthy": 2,       ✅ 2个异常
    "today_restarts": 4
  },
  "monitors": [
    {"name": "27币涨跌幅追踪", "status": "healthy", ...},
    {"name": "1小时爆仓金额", "status": "healthy", ...},
    {"name": "恐慌清洗指数", "status": "healthy", ...},
    {"name": "锚点盈利统计", "status": "healthy", ...},
    {"name": "逃顶信号统计", "status": "healthy", ...},
    {"name": "支撑压力线系统", "status": "healthy", ...},
    {"name": "SAR斜率系统", "status": "unhealthy", ...},      ✅ 新增显示
    {"name": "Google Drive监控", "status": "unhealthy", ...}  ✅ 新增显示
  ]
}
```

### 2. 页面测试 ✅

访问：https://5000-ikmpd2up5chrwx4jjjkih-5634da27.sandbox.novita.ai/data-health-monitor

- ✅ 页面加载成功（7.74秒）
- ✅ 显示8个服务卡片
- ✅ 统计正确（8/6/2/4）
- ✅ 异常服务显示为红色❌状态

## 对比表格

| 项目 | 修复前 | 修复后 | 状态 |
|------|--------|--------|------|
| API返回服务数 | 6 | 8 | ✅ |
| 页面显示服务数 | 6 | 8 | ✅ |
| SAR斜率系统 | ❌ 缺失 | ✅ 显示 | ✅ |
| Google Drive监控 | ❌ 缺失 | ✅ 显示 | ✅ |
| 统计准确性 | 不一致 | 一致 | ✅ |

## 监控服务完整清单

### 配置来源
- **监控配置**：`source_code/data_health_monitor.py` 中的 `MONITORS` 字典
- **API端点**：`source_code/app_new.py` 中的 `monitor_configs` 字典（已修复）

### 8个监控服务

| # | 服务名称 | PM2名称 | 数据源API | 延迟阈值 | 当前状态 |
|---|---------|---------|----------|---------|---------|
| 1 | 27币涨跌幅追踪 | coin-change-tracker | /api/coin-change-tracker/history | 5分钟 | ✅ 健康 |
| 2 | 1小时爆仓金额 | liquidation-1h-collector | /api/panic/hour1-curve | 5分钟 | ✅ 健康 |
| 3 | 恐慌清洗指数 | panic-collector | /api/panic/latest | 5分钟 | ✅ 健康 |
| 4 | 锚点盈利统计 | anchor-profit-monitor | /api/anchor-system/profit-history | 5分钟 | ✅ 健康 |
| 5 | 逃顶信号统计 | escape-signal-calculator | /api/escape-signal-stats/keypoints | 5分钟 | ✅ 健康 |
| 6 | 支撑压力线系统 | support-resistance-collector | 仅PM2状态 | 5分钟 | ✅ 健康 |
| 7 | SAR斜率系统 | sar-jsonl-collector | /api/sar-slope/latest | 10分钟 | ❌ 异常 |
| 8 | Google Drive监控 | gdrive-detector | /api/gdrive-detector/status | 15分钟 | ❌ 异常 |

## 异常服务排查

### SAR斜率系统（数据延迟153分钟）

**问题**：数据采集中断，最后更新时间超过2.5小时

**可能原因**：
1. API返回数据格式变化
2. 数据源接口异常
3. 采集器代码逻辑错误

**排查步骤**：
```bash
# 1. 检查服务日志
pm2 logs sar-jsonl-collector --lines 50

# 2. 测试API
curl -s "http://localhost:5000/api/sar-slope/latest" | jq

# 3. 手动重启
pm2 restart sar-jsonl-collector
```

### Google Drive监控（数据延迟29分钟）

**问题**：Google Drive TXT文件未更新

**可能原因**：
1. Google Drive同步停止
2. 数据源端（桌面应用）未生成新文件
3. Google Drive API限流

**排查步骤**：
```bash
# 1. 检查监控日志
pm2 logs gdrive-detector --lines 50

# 2. 检查最新文件时间
curl -s "http://localhost:5000/api/gdrive-detector/status" | jq

# 3. 手动重启
pm2 restart gdrive-detector
```

## 文件变更清单

### 修改的文件
1. `/home/user/webapp/source_code/app_new.py`
   - 修改：添加SAR斜率系统和Google Drive监控到 `monitor_configs`

### 文档
2. `/home/user/webapp/DATA_HEALTH_MONITOR_DISPLAY_FIX.md` - 本修复报告

## 技术要点

### 1. 配置同步问题

**问题**：监控配置在两处定义
- `data_health_monitor.py` - 监控进程配置（8个）
- `app_new.py` - API端点配置（原6个）

**风险**：容易不同步

**建议**：
- 统一配置到一个文件
- 或者从状态文件动态读取
- 添加配置校验

### 2. 硬编码的危害

**案例**：本次问题就是硬编码导致的

**教训**：
- 避免重复定义配置
- 使用动态读取
- 添加单元测试验证配置完整性

### 3. 监控可见性

**重要性**：异常服务也需要显示

**原因**：
- 用户需要知道哪些服务异常
- 异常服务需要手动干预
- 隐藏异常会掩盖问题

## 系统状态

✅ **修复完成时间**：2026-02-01 17:00:00
✅ **系统运行状态**：🟢 正常
✅ **监控完整性**：100% (8/8)
✅ **页面显示**：正确

### 当前监控状态
- **总数**：8个服务
- **健康**：6个（75%）
- **异常**：2个（25%）
  - SAR斜率系统：数据延迟153分钟
  - Google Drive监控：数据延迟29分钟
- **今日重启**：4次

### 后续行动

1. ✅ **立即**：修复完成，页面正确显示8个服务
2. ⏳ **短期**：排查SAR和Google Drive的数据中断原因
3. ⏳ **中期**：优化监控配置，避免硬编码
4. ⏳ **长期**：添加配置校验和自动化测试

## 相关文档

- 📄 DATA_SYNC_COMPLETE_FIX_REPORT.md - 数据同步修复
- 📄 ROUND_RUSH_DATA_FIX_REPORT.md - 本轮数据修复
- 📄 TAO_TRX_FIX_COMPLETE_REPORT.md - TAO/TRX采集修复
- 📄 HEALTH_MONITOR_LINK_UPDATE.md - 健康监控链接更新
- 📄 SAR_BIAS_HEALTH_MONITOR_REPORT.md - SAR健康监控

## 总结

### 核心问题
API端点硬编码配置，只包含6个服务，缺少SAR和Google Drive

### 解决方案
在 `monitor_configs` 中添加缺失的2个服务

### 效果
- ✅ API返回从6个增加到8个
- ✅ 页面显示从6个增加到8个
- ✅ 统计数据与实际一致
- ✅ 异常服务正确显示

### 教训
1. 避免硬编码配置
2. 配置应统一管理
3. 添加配置校验
4. 异常状态也要显示

---

**修复完成**: 2026-02-01 17:00:00  
**系统状态**: 🟢 正常运行  
**监控完整性**: ✅ 8/8 (100%)  
**用户影响**: ✅ 问题完全解决
