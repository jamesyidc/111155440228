# 日内模式监控系统 - 完整架构说明

## 系统架构

### 1. 实时监控器（后台服务）
- **文件**: `monitors/intraday_pattern_realtime_monitor.py`
- **功能**: 每10分钟检测最新的4根10分钟柱子
- **运行时间**: 每天 2:00 - 23:59
- **数据流向**:
  ```
  实时数据 → 检测模式 → 判断是否满足条件
  ├─ 满足条件 → 发送3次TG通知 + 追加写入JSONL
  └─ 不满足条件 → 只追加写入JSONL（不发TG）
  ```

### 2. 数据存储（JSONL文件）
- **路径**: `data/intraday_patterns/all_detections_<date>.jsonl`
- **格式**: 每行一个JSON对象，记录一个检测到的模式
- **写入模式**: **追加写入**（append），同一天的检测结果累积在同一个文件中
- **数据内容**:
  ```json
  {
    "timestamp": "2026-02-25T17:24:06",
    "date": "2026-02-25",
    "detection_time": "2026-02-25 17:24:06",
    "pattern_type": "pattern_1_3",
    "pattern_name": "诱多等待新低",
    "bar_type": "红→黄→绿 (3根)",
    "signal": "预高做空",
    "time_range": "04:50-05:10",
    "bars": [...],
    "trigger_ratio": 72.3,
    "threshold": 65.0,
    "satisfied": true  // 是否满足触发条件
  }
  ```

### 3. 网页显示（前端）
- **页面**: `/coin-change-tracker`
- **API**: `/api/intraday-patterns/all-detections/<date>`
- **数据来源**: 直接读取JSONL文件（无需实时计算）
- **显示逻辑**:
  - ✅ **满足触发条件的模式**（绿色边框）
  - ⚠️ **不满足触发条件的模式**（黄色边框，显示失败原因）

## 工作流程

### 流程图
```
┌─────────────────────────────────────────────────────────────┐
│                    实时监控器 (每10分钟)                      │
│                                                               │
│  1. 读取最新4根10分钟柱子 ─────────────────────┐              │
│                                                │              │
│  2. 检测模式（红→黄→绿 等组合）                │              │
│                                                │              │
│  3. 判断是否满足触发条件                      │              │
│     ├─ 满足条件？                              │              │
│     │   ├─ YES → 发送3次TG通知 ───────────────┼──> TG群     │
│     │   └─ YES → 写入JSONL ───────────────────┼──┐          │
│     └─ 不满足条件？                            │   │          │
│         └─ YES → 写入JSONL ────────────────────┼──┤          │
│                                                │   │          │
└────────────────────────────────────────────────┼───┼──────────┘
                                                 │   │
                                                 ▼   ▼
                                    ┌─────────────────────────┐
                                    │  JSONL文件（追加模式）   │
                                    │  all_detections_<date>  │
                                    └─────────────────────────┘
                                                 │
                                                 │ 读取
                                                 ▼
                                    ┌─────────────────────────┐
                                    │   网页前端（实时显示）   │
                                    │   - 满足条件（绿色）     │
                                    │   - 不满足条件（黄色）   │
                                    └─────────────────────────┘
```

## 检测模式说明

### 模式1: 诱多等待新低
- **组合**:
  - 3根: 红→黄→绿 或 绿→黄→红
  - 4根: 红→黄→黄→绿
- **触发条件**:
  - 预判"等待新低": 最后一根柱子上涨占比 ≥ 65%
  - 预判"做空/观望": 最后一根柱子上涨占比 ≥ 50%
- **信号**: 预高做空

### 模式3: 筑底信号
- **组合**: 黄→绿→黄 (3根)
- **触发条件**:
  - 最后一根柱子上涨占比 < 10%
  - **且** 当日涨跌幅总和 < -50%
- **信号**: 预低做多

### 模式4: 诱空信号
- **组合**:
  - 3根: 绿→红→绿
  - 4根: 绿→红→红→绿
- **触发条件**: 中间所有红柱子上涨占比 < 10%
- **信号**: 预低做多

## 部署说明

### 1. 启动实时监控器

#### 方式一: 直接运行（测试）
```bash
cd /home/user/webapp
python3 monitors/intraday_pattern_realtime_monitor.py
```

#### 方式二: 后台运行（生产）
```bash
cd /home/user/webapp
nohup python3 monitors/intraday_pattern_realtime_monitor.py > logs/pattern_monitor.log 2>&1 &
```

#### 方式三: 使用PM2（推荐）
```bash
cd /home/user/webapp
pm2 start monitors/intraday_pattern_realtime_monitor.py --name "intraday-pattern-monitor" --interpreter python3
pm2 save
pm2 startup
```

### 2. 查看监控状态

#### 检查进程
```bash
ps aux | grep intraday_pattern_realtime_monitor
```

#### 查看日志
```bash
# PM2方式
pm2 logs intraday-pattern-monitor --lines 50

# nohup方式
tail -f logs/pattern_monitor.log
```

### 3. 停止监控器

#### 直接运行方式
按 `Ctrl+C`

#### 后台运行方式
```bash
pkill -f intraday_pattern_realtime_monitor
```

#### PM2方式
```bash
pm2 stop intraday-pattern-monitor
pm2 delete intraday-pattern-monitor
```

## 数据文件说明

### JSONL文件结构
```
data/intraday_patterns/
├── all_detections_2026-02-23.jsonl  # 2月23日的所有检测结果
├── all_detections_2026-02-24.jsonl  # 2月24日的所有检测结果
└── all_detections_2026-02-25.jsonl  # 2月25日的所有检测结果
```

### 追加写入特性
- **同一天**: 所有检测结果追加到同一个文件中
- **每次检测**: 如果检测到模式，立即追加一行
- **历史保留**: 旧的检测结果不会被覆盖

### 查看JSONL文件
```bash
# 查看今天的检测结果
cat data/intraday_patterns/all_detections_2026-02-25.jsonl | python3 -m json.tool

# 统计今天检测到的模式数量
wc -l data/intraday_patterns/all_detections_2026-02-25.jsonl

# 只查看满足条件的模式
cat data/intraday_patterns/all_detections_2026-02-25.jsonl | grep '"satisfied": true'
```

## API说明

### 获取指定日期的检测结果
```bash
GET /api/intraday-patterns/all-detections/<date>
```

**示例**:
```bash
curl http://localhost:9002/api/intraday-patterns/all-detections/2026-02-25
```

**返回格式**:
```json
{
  "success": true,
  "date": "2026-02-25",
  "source": "jsonl",
  "qualified_patterns": [...],    // 满足条件的模式列表
  "unqualified_patterns": [...],  // 不满足条件的模式列表
  "summary": {
    "total_count": 5,
    "qualified_count": 1,
    "unqualified_count": 4
  },
  "total_bars": 132,
  "total_change": 87.87,
  "daily_prediction": "等待新低"
}
```

## 监控和维护

### 健康检查

#### 1. 检查监控器是否运行
```bash
ps aux | grep intraday_pattern_realtime_monitor | grep -v grep
```

#### 2. 检查今天是否有检测记录
```bash
ls -lh data/intraday_patterns/all_detections_$(date +%Y-%m-%d).jsonl
```

#### 3. 检查最新检测时间
```bash
tail -1 data/intraday_patterns/all_detections_$(date +%Y-%m-%d).jsonl | python3 -c "import json, sys; print(json.load(sys.stdin)['detection_time'])"
```

### 常见问题排查

#### 问题1: 监控器没有运行
**解决方案**:
```bash
cd /home/user/webapp
nohup python3 monitors/intraday_pattern_realtime_monitor.py > logs/pattern_monitor.log 2>&1 &
```

#### 问题2: 没有检测到模式
**原因**: 可能当前市场没有形成指定的颜色组合
**检查方式**:
```bash
# 查看最新的4根柱子
python3 -c "
from monitors.intraday_pattern_realtime_monitor import get_latest_bars
bars, total_change, prediction = get_latest_bars(4)
for bar in bars:
    print(f\"{bar['emoji']} {bar['time']} - {bar['up_ratio']}% ({bar['color']})\")
"
```

#### 问题3: TG通知没有发送
**检查**:
1. 监控器日志中是否有"发送TG通知"
2. 检查TELEGRAM_BOT_TOKEN和TELEGRAM_CHAT_ID配置
3. 确认模式是否真正满足触发条件（`satisfied: true`）

#### 问题4: 页面不显示检测结果
**解决方案**:
1. 检查JSONL文件是否存在且有数据
2. 检查Flask服务是否正常运行
3. 清除浏览器缓存（Ctrl+Shift+R）

## 与旧系统的对比

| 特性 | 旧系统 | 新系统 |
|------|--------|--------|
| 检测时机 | 每天生成一次 | 每10分钟实时检测 |
| 数据存储 | 覆盖写入 | 追加写入（累积） |
| TG通知 | 所有检测到的都发送 | 只有满足条件的才发送 |
| 网页显示 | 需要手动生成 | 自动累积显示 |
| 失败原因 | 不记录 | 详细记录 |
| 数据一致性 | 可能被覆盖 | 历史记录完整保留 |

## 总结

✅ **实时监控**: 每10分钟自动检测最新的4根柱子
✅ **智能通知**: 只有满足触发条件的才发送TG通知
✅ **完整记录**: 所有检测到的模式都写入JSONL
✅ **分类显示**: 网页端分别显示满足和不满足条件的模式
✅ **累积存储**: JSONL文件按日期追加写入，历史记录不丢失
✅ **高性能**: 网页端直接读取JSONL，无需实时计算

系统现在完全符合你的需求！🎉
