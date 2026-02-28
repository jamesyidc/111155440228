# 日内模式检测结果每日生成配置

## 功能说明

该系统实现了日内模式检测结果的按天存储功能，提高了系统可靠性和性能：

1. **数据持久化**：检测结果存储在JSONL文件中，避免重复计算
2. **快速响应**：API优先从文件读取，提升页面加载速度
3. **历史一致性**：历史数据不会因算法调整而变化
4. **分类显示**：同时保存满足和不满足触发条件的模式

## 文件存储位置

```
data/intraday_patterns/all_detections_<date>.jsonl
```

例如：`data/intraday_patterns/all_detections_2026-02-25.jsonl`

## 数据格式

每个JSONL文件包含一行JSON记录：

```json
{
  "timestamp": "2026-02-25T09:11:09.214079",
  "date": "2026-02-25",
  "daily_prediction": "等待新低",
  "total_bars": 132,
  "total_change": 81.16,
  "summary": {
    "total_count": 0,
    "qualified_count": 0,
    "unqualified_count": 0
  },
  "qualified_patterns": [],
  "unqualified_patterns": []
}
```

## 使用方法

### 1. 手动生成

#### 生成今天的检测结果：
```bash
cd /home/user/webapp
python3 scripts/generate_all_patterns_daily.py
```

#### 生成指定日期的检测结果：
```bash
python3 scripts/generate_all_patterns_daily.py --date 2026-02-25
```

#### 批量回填历史数据：
```bash
python3 scripts/generate_all_patterns_daily.py --backfill --start-date 2026-02-01 --end-date 2026-02-25
```

### 2. 设置每日自动生成（Cron）

#### 方式一：使用系统crontab

编辑crontab：
```bash
crontab -e
```

添加以下任务（每天23:59执行）：
```cron
59 23 * * * cd /home/user/webapp && /usr/bin/python3 scripts/generate_all_patterns_daily.py >> /home/user/webapp/logs/pattern_generation.log 2>&1
```

或者每天凌晨0:01执行前一天的数据：
```cron
1 0 * * * cd /home/user/webapp && /usr/bin/python3 scripts/generate_all_patterns_daily.py --date $(date -d "yesterday" +\%Y-\%m-\%d) >> /home/user/webapp/logs/pattern_generation.log 2>&1
```

#### 方式二：使用Python APScheduler

在 `monitors/` 目录下创建定时任务脚本，参考现有监控器的实现。

### 3. API使用

API会自动优先从JSONL文件读取数据，如果文件不存在才实时计算。

#### 获取指定日期的检测结果：
```bash
GET /api/intraday-patterns/all-detections/<date>
```

示例：
```bash
curl http://localhost:9002/api/intraday-patterns/all-detections/2026-02-25
```

返回数据包含 `source` 字段：
- `"source": "jsonl"` - 数据来自JSONL文件
- `"source": "realtime"` - 实时计算的数据

## 监控和维护

### 检查生成状态

查看日志文件：
```bash
tail -f /home/user/webapp/logs/pattern_generation.log
```

### 检查JSONL文件

列出所有检测结果文件：
```bash
ls -lh data/intraday_patterns/all_detections_*.jsonl
```

查看特定日期的结果：
```bash
cat data/intraday_patterns/all_detections_2026-02-25.jsonl | python3 -m json.tool
```

### 清理旧文件

保留最近90天的数据（可根据需要调整）：
```bash
find data/intraday_patterns/ -name "all_detections_*.jsonl" -mtime +90 -delete
```

## 故障排查

### 问题：脚本执行失败

**解决方案**：
1. 检查数据文件是否存在：`data/coin_change_tracker/coin_change_<date>.jsonl`
2. 检查预判文件：`data/daily_predictions/prediction_<date>.json`
3. 查看错误日志：`logs/pattern_generation.log`

### 问题：API返回空数据

**解决方案**：
1. 检查JSONL文件是否存在
2. 手动运行生成脚本
3. 检查Flask日志：`/tmp/flask_app.log`

### 问题：历史数据缺失

**解决方案**：
使用批量回填功能：
```bash
python3 scripts/generate_all_patterns_daily.py --backfill --start-date 2026-02-01 --end-date 2026-02-25
```

## 性能优化

1. **分页读取**：如果需要读取多个日期的数据，建议使用批量API
2. **缓存策略**：前端可以缓存历史日期的结果（这些不会改变）
3. **压缩存储**：可以考虑使用gzip压缩JSONL文件以节省空间

## 升级和迁移

### 从旧格式迁移

如果已有旧的 `detections_<date>.jsonl` 文件（只包含满足条件的模式），可以重新生成包含所有模式的新文件：

```bash
python3 scripts/generate_all_patterns_daily.py --backfill --start-date 2026-02-01
```

## 常见命令速查

| 命令 | 说明 |
|------|------|
| `python3 scripts/generate_all_patterns_daily.py` | 生成今天的结果 |
| `python3 scripts/generate_all_patterns_daily.py --date 2026-02-25` | 生成指定日期 |
| `python3 scripts/generate_all_patterns_daily.py --backfill --start-date 2026-02-01` | 回填历史数据 |
| `ls -lh data/intraday_patterns/all_detections_*.jsonl` | 查看所有文件 |
| `cat data/intraday_patterns/all_detections_2026-02-25.jsonl \| python3 -m json.tool` | 查看文件内容 |
| `curl http://localhost:9002/api/intraday-patterns/all-detections/2026-02-25` | 测试API |

## 注意事项

1. ⚠️ **数据一致性**：生成后的JSONL文件不应手动编辑
2. ⚠️ **磁盘空间**：定期清理旧文件以节省空间
3. ⚠️ **时区问题**：所有时间使用北京时间（Asia/Shanghai）
4. ✅ **幂等性**：多次运行同一日期会覆盖旧文件，可以安全重新生成
5. ✅ **向后兼容**：即使JSONL文件不存在，API也会自动实时计算
