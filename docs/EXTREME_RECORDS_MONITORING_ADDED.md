# 历史极值记录 - 添加到数据采集健康监控

## 完成时间
2026-02-01 21:50 (北京时间)

## 添加的监控项

### 历史极值记录
- **监控名称**: 历史极值记录
- **PM2服务名**: `extreme-monitor-jsonl`
- **数据API**: `http://localhost:5000/api/anchor-system/profit-records-with-coins?trade_mode=real&limit=1`
- **时间字段**: `timestamp` (records[0].timestamp)
- **数据路径**: `['records', 0]` (取第一条记录)
- **最大延迟**: 10分钟 (极值事件不频繁)
- **检查间隔**: 60秒
- **自动重启**: ✅ 启用
- **Telegram通知**: ✅ 启用

## 监控状态

### 当前检测结果
```
🔍 检查服务: 历史极值记录
============================================================
❌ 服务 extreme-monitor-jsonl 不存在或无法获取状态
```

### 服务状态
- **PM2服务**: ❌ 未运行 (`extreme-monitor-jsonl` 不存在)
- **数据文件**: ❌ 空文件 (`data/extreme_jsonl/extreme_real.jsonl` 为空)
- **今日分区**: ❌ 不存在 (`extreme_real_20260201.jsonl` 未创建)
- **API状态**: ✅ 正常 (返回空数据)
- **前端页面**: ✅ 正常 (显示"暂无历史记录")

## 数据流程

```
极值监控服务 (extreme_monitor_jsonl.py)
    ↓
JSONL文件 (extreme_real_YYYYMMDD.jsonl)
    ↓
ExtremeDailyJSONLManager
    ↓
API (/api/anchor-system/profit-records-with-coins)
    ↓
前端页面 (anchor-system-real)
```

### 当前状态
```
❌ 未运行 → ❌ 无数据 → ✅ API正常 → ✅ 显示"暂无记录"
```

## 健康监控系统

### 监控配置文件
- **文件**: `source_code/data_health_monitor.py`
- **配置位置**: `MONITORS` 字典
- **总监控项**: 10个

### 所有监控项列表
1. ✅ 27币涨跌幅追踪 (`coin-change-tracker`)
2. ✅ 1小时爆仓金额 (`liquidation-1h-collector`)
3. ✅ 恐慌清洗指数 (`panic-collector`)
4. ✅ 锚点盈利统计 (`anchor-profit-monitor`)
5. ✅ 逃顶信号统计 (`escape-signal-calculator`)
6. ✅ 支撑压力线系统 (`support-resistance-collector`)
7. ✅ SAR斜率系统 (`sar-jsonl-collector`)
8. ✅ Google Drive监控 (`gdrive-detector`)
9. ✅ SAR偏向统计 (`sar-bias-stats-collector`)
10. ✅ 透明标签快照 (`gdrive-detector`)
11. **🆕 历史极值记录** (`extreme-monitor-jsonl`) ⚠️ **服务未运行**

## 监控工作流程

### 检查逻辑
1. **PM2状态检查**: 检查服务是否在线
   - 当前结果: ❌ 服务不存在
2. **数据新鲜度检查**: 检查最新数据时间戳
   - 跳过 (服务不存在)
3. **自动修复**: 如果数据过期且服务在线，自动重启
   - 跳过 (服务不存在)
4. **Telegram通知**: 发送异常通知
   - ⚠️ 会通知服务不存在

### 监控日志
```bash
# 查看监控日志
pm2 logs data-health-monitor --lines 50

# 查看状态文件
cat data/data_health_monitor_state.json
```

## 启动极值监控服务 (可选)

### 如果需要极值记录功能

1. **检查服务脚本**
```bash
ls -la source_code/extreme_monitor_jsonl.py
```

2. **添加到ecosystem.config.js**
```javascript
{
  name: 'extreme-monitor-jsonl',
  script: 'source_code/extreme_monitor_jsonl.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  autorestart: true,
  max_restarts: 10,
  min_uptime: '10s'
}
```

3. **启动服务**
```bash
pm2 start ecosystem.config.js --only extreme-monitor-jsonl
pm2 save
```

4. **验证数据采集**
```bash
# 等待几分钟后检查
ls -lh data/extreme_jsonl/
tail -f data/extreme_jsonl/extreme_real_$(date +%Y%m%d).jsonl
```

## 验证监控功能

### 查看监控页面
🔗 **数据采集健康监控**: https://5000-ikmpd2up5chrwx4jjjkih-5634da27.sandbox.novita.ai/data-health-monitor

### 预期显示
- ✅ 总监控项: 10个
- ⚠️ **历史极值记录**: 显示为"错误"或"服务不存在"
- 📊 其他9个服务: 显示为"健康"

### API测试
```bash
# 查看监控状态
curl -s "http://localhost:5000/api/data-health-monitor/status" | python3 -m json.tool

# 查看极值记录API
curl -s "http://localhost:5000/api/anchor-system/profit-records-with-coins?trade_mode=real&limit=1"
```

## 修改内容

### 文件修改
- **文件**: `source_code/data_health_monitor.py`
- **修改行数**: +12行
- **修改内容**: 在 `MONITORS` 字典中添加"历史极值记录"配置

### 服务重启
```bash
pm2 restart data-health-monitor
```

## 结论

### ✅ 已完成
1. ✅ 在健康监控系统中添加"历史极值记录"监控项
2. ✅ 配置正确的API端点和数据路径
3. ✅ 启用自动重启和Telegram通知
4. ✅ 验证监控系统正常检测服务状态

### ⚠️ 当前状态
- **监控功能**: ✅ 已添加并正常工作
- **极值监控服务**: ❌ 未运行 (需要手动启动)
- **数据采集**: ❌ 无数据 (服务未运行)
- **页面显示**: ✅ 正常 (显示"暂无历史记录")

### 📝 建议
- 如果需要极值记录功能，请按照上述步骤启动 `extreme-monitor-jsonl` 服务
- 如果不需要，当前配置可以保留，监控系统会报告服务缺失
- 健康监控会定期检查并在服务启动后自动恢复正常

---

**历史极值记录已成功添加到数据采集健康监控系统！**
