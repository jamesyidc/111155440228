# 新高新低统计系统 - 部署和问题排查指南

## 📋 问题现象

用户反馈：每次重新部署后，新高新低统计页面显示没有数据。

## 🔍 根本原因分析

经过深入检查，系统**当前运行正常**，但找到了可能导致重新部署后数据丢失的根本原因：

### 1. 依赖链条分析

```
价格数据采集 → 新高新低检测 → API返回 → 前端显示
     ↓              ↓              ↓          ↓
price-position  new-high-low   Flask API   网页
 collector      collector    (需重启生效)  (缓存问题)
```

### 2. 可能的失败点

#### 失败点1：price-position-collector未运行 ❌
- **症状**：data/price_position/目录下没有今天的JSONL文件
- **原因**：price-position-collector进程未启动或崩溃
- **影响**：new-high-low-collector没有数据源
- **检查命令**：
```bash
pm2 list | grep price-position
ls -lh data/price_position/price_position_$(date +%Y%m%d).jsonl
```

#### 失败点2：new-high-low-collector未运行 ❌
- **症状**：data/new_high_low/目录下没有今天的JSONL文件
- **原因**：new-high-low-collector进程未启动
- **影响**：API无法获取今天的数据
- **检查命令**：
```bash
pm2 list | grep new-high-low
ls -lh data/new_high_low/new_high_low_events_$(date +%Y%m%d).jsonl
```

#### 失败点3：Flask未重启 ❌
- **症状**：API返回旧数据或错误
- **原因**：Flask缓存了旧的数据文件路径
- **影响**：前端获取不到最新数据
- **检查命令**：
```bash
pm2 list | grep flask
curl -s "http://localhost:9002/api/price-position/new-high-low-stats" | python3 -m json.tool
```

#### 失败点4：浏览器缓存 ❌
- **症状**：API返回正常但页面显示旧数据
- **原因**：浏览器缓存了旧的JS/HTML
- **影响**：页面显示错误
- **解决方法**：Ctrl+F5强制刷新

---

## ✅ 当前系统状态（2026-02-28）

### 1. 数据采集器状态
```bash
$ pm2 list | grep -E "price-position|new-high-low"
│ 22 │ price-position-collector  │ online │ 112.4mb │ ← 运行正常
│ 27 │ new-high-low-collector    │ online │   5.7mb │ ← 运行正常
```

### 2. 数据文件状态
```bash
$ ls -lh data/price_position/price_position_20260228.jsonl
-rw-r--r-- 1 user user 3.0M Feb 28 13:01  ← 数据源正常

$ ls -lh data/new_high_low/new_high_low_events_20260228.jsonl
-rw-r--r-- 1 user user 5.4K Feb 28 12:59  ← 事件记录正常

$ wc -l data/new_high_low/new_high_low_events_20260228.jsonl
30  ← 今天已有30条事件
```

### 3. API响应状态
```bash
$ curl -s "http://localhost:9002/api/price-position/new-high-low-stats" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); \
  print(f\"Today: {d['today']['total_events']} events\")"

Today: 30 events  ← API返回正常
```

### 4. 前端页面状态
```
访问: https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/new-high-low-stats

控制台日志:
✅ [New High/Low] 数据加载成功: {
    timestamp: 2026-02-28 21:02:07,
    coin_count: 28,
    today_events: 30,
    seven_days_events: 863
}
✅ [New High/Low] 页面更新完成

结论: 页面正常显示
```

---

## 🚀 正确的部署流程

### 步骤1：停止所有PM2进程（可选）
```bash
pm2 stop all
```

### 步骤2：拉取最新代码
```bash
cd /home/user/webapp
git pull origin main
```

### 步骤3：检查PM2配置是否包含new-high-low-collector
```bash
grep -A 10 "new-high-low-collector" ecosystem.config.js
```

如果没有，手动添加：
```javascript
{
  name: 'new-high-low-collector',
  script: 'source_code/new_high_low_collector.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  autorestart: true,
  watch: false,
  max_memory_restart: '300M',
  error_file: '/home/user/webapp/logs/new-high-low-error.log',
  out_file: '/home/user/webapp/logs/new-high-low-out.log',
  log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
}
```

### 步骤4：启动所有服务
```bash
pm2 start ecosystem.config.js
```

**或者**如果已经运行，只需重新加载配置：
```bash
pm2 reload ecosystem.config.js
```

### 步骤5：保存PM2配置（重要！）
```bash
pm2 save
```

### 步骤6：验证所有服务运行
```bash
pm2 list
```

确保看到：
```
│ 22 │ price-position-collector  │ online │
│ 27 │ new-high-low-collector    │ online │
│ 0  │ flask-app                 │ online │
```

### 步骤7：等待数据采集（3-5分钟）
```bash
# 查看new-high-low-collector日志
pm2 logs new-high-low-collector --lines 20

# 应该看到类似输出：
# ✅ 检测到 N 个新事件
# ✅ 状态文件已保存
```

### 步骤8：验证数据文件
```bash
# 检查今天的事件文件
TODAY=$(date +%Y%m%d)
ls -lh data/new_high_low/new_high_low_events_${TODAY}.jsonl
wc -l data/new_high_low/new_high_low_events_${TODAY}.jsonl
```

### 步骤9：测试API
```bash
curl -s "http://localhost:9002/api/price-position/new-high-low-stats" \
  | python3 -m json.tool | head -30
```

检查输出中的 `today.total_events` 是否 > 0

### 步骤10：清除浏览器缓存并刷新页面
- 按 `Ctrl + Shift + Delete` 清除缓存
- 或按 `Ctrl + F5` 强制刷新
- 打开控制台查看是否有错误

---

## 🔧 故障排查步骤

### 问题：页面显示"没有数据"

#### 步骤1：检查采集器是否运行
```bash
pm2 list | grep -E "price-position|new-high-low"
```

**预期结果**：两个进程都应该是 `online` 状态

**如果offline**：
```bash
pm2 restart price-position-collector
pm2 restart new-high-low-collector
```

#### 步骤2：检查数据文件是否存在
```bash
TODAY=$(date +%Y%m%d)
ls -lh data/price_position/price_position_${TODAY}.jsonl
ls -lh data/new_high_low/new_high_low_events_${TODAY}.jsonl
```

**预期结果**：两个文件都应该存在且大小 > 0

**如果文件不存在**：
```bash
# 查看price-position-collector日志
pm2 logs price-position-collector --lines 50

# 查看new-high-low-collector日志
pm2 logs new-high-low-collector --lines 50
```

#### 步骤3：检查API响应
```bash
curl -s "http://localhost:9002/api/price-position/new-high-low-stats" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); \
  print('Success:', d.get('success')); \
  print('Today events:', d.get('today', {}).get('total_events', 0)); \
  print('Timestamp:', d.get('timestamp'))"
```

**预期结果**：
```
Success: True
Today events: > 0
Timestamp: 2026-02-28 XX:XX:XX
```

**如果success=False**：
```bash
# 重启Flask
pm2 restart flask-app
sleep 5
# 再次测试
```

#### 步骤4：检查前端控制台
打开浏览器控制台（F12），查看：
- 是否有JS错误
- API请求是否成功（Network标签）
- 控制台是否显示"数据加载成功"

**如果看到错误**：
- 清除浏览器缓存（Ctrl+Shift+Delete）
- 强制刷新（Ctrl+F5）
- 检查是否被浏览器插件拦截

---

## 📊 数据流程图

```
┌─────────────────────────────────────────────────────┐
│   Step 1: 价格数据采集                               │
│   price-position-collector (每3分钟)                │
│   ↓                                                  │
│   data/price_position/price_position_YYYYMMDD.jsonl │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│   Step 2: 新高新低检测                               │
│   new-high-low-collector (每3分钟)                  │
│   读取: price_position_YYYYMMDD.jsonl              │
│   比较: coin_highs_lows_state.json (历史极值)      │
│   ↓                                                  │
│   检测创新高/创新低事件                              │
│   ↓                                                  │
│   写入: new_high_low_events_YYYYMMDD.jsonl         │
│   更新: coin_highs_lows_state.json                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│   Step 3: API数据聚合                                │
│   Flask API: /api/price-position/new-high-low-stats│
│   读取: new_high_low_events_*.jsonl (过去8天)       │
│   读取: coin_highs_lows_state.json                 │
│   ↓                                                  │
│   统计: 今天、昨天、3天、7天的新高新低事件           │
│   ↓                                                  │
│   返回: JSON响应                                     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│   Step 4: 前端展示                                   │
│   网页: /new-high-low-stats                         │
│   fetch API → 解析数据 → 更新DOM → 渲染图表        │
└─────────────────────────────────────────────────────┘
```

---

## 🛡️ 防止数据丢失的措施

### 1. Git版本控制
所有重要数据文件都应该提交到Git：
```bash
# 检查哪些数据文件在Git中
git ls-files | grep new_high_low

# 应该包括：
# - coin_highs_lows_state.json (状态文件)
# - new_high_low_events_*.jsonl (事件记录)
```

### 2. PM2自动启动
确保PM2配置已保存：
```bash
pm2 save

# 验证保存的配置
cat ~/.pm2/dump.pm2 | python3 -c \
  "import json,sys; names=[p['name'] for p in json.load(sys.stdin)]; \
  print('new-high-low-collector' in names)"

# 应该输出: True
```

### 3. 数据备份
定期备份重要数据文件：
```bash
# 创建备份脚本
cat > scripts/backup_new_high_low.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/user/webapp/backups/new_high_low"
TODAY=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
cp data/new_high_low/coin_highs_lows_state.json $BACKUP_DIR/state_$TODAY.json
tar -czf $BACKUP_DIR/events_$TODAY.tar.gz data/new_high_low/*.jsonl
echo "✅ Backup completed: $BACKUP_DIR"
EOF

chmod +x scripts/backup_new_high_low.sh
```

### 4. 健康监控
添加定时任务检查系统健康：
```bash
# 创建健康检查脚本
cat > scripts/health_check_new_high_low.sh << 'EOF'
#!/bin/bash
TODAY=$(date +%Y%m%d)
DATA_FILE="data/new_high_low/new_high_low_events_${TODAY}.jsonl"

if [ ! -f "$DATA_FILE" ]; then
    echo "❌ ERROR: Today's data file missing: $DATA_FILE"
    # 发送告警通知（可选）
    exit 1
fi

EVENT_COUNT=$(wc -l < "$DATA_FILE")
if [ $EVENT_COUNT -eq 0 ]; then
    echo "⚠️  WARNING: Today's data file is empty: $DATA_FILE"
    exit 1
fi

echo "✅ OK: $EVENT_COUNT events recorded today"
exit 0
EOF

chmod +x scripts/health_check_new_high_low.sh
```

---

## 📝 维护建议

### 每日检查清单
```bash
# 1. 检查所有进程运行状态
pm2 list

# 2. 查看今天的数据文件
TODAY=$(date +%Y%m%d)
ls -lh data/new_high_low/new_high_low_events_${TODAY}.jsonl

# 3. 测试API
curl -s "http://localhost:9002/api/price-position/new-high-low-stats" | \
  python3 -m json.tool | grep -E "success|today|timestamp"

# 4. 查看采集器日志（最后10行）
pm2 logs new-high-low-collector --lines 10
```

### 每周维护任务
```bash
# 1. 清理30天前的旧数据
find data/new_high_low/ -name "new_high_low_events_*.jsonl" -mtime +30 -delete

# 2. 检查磁盘空间
df -h /home/user/webapp

# 3. 重启长时间运行的进程（可选）
pm2 restart new-high-low-collector
pm2 restart price-position-collector
```

---

## ✅ 总结

### 当前系统状态：完全正常 ✅
- ✅ price-position-collector 运行正常
- ✅ new-high-low-collector 运行正常
- ✅ 今天有30个事件记录
- ✅ API响应正常
- ✅ 前端页面显示正常

### 重新部署时的关键步骤：
1. ✅ 确保ecosystem.config.js包含new-high-low-collector
2. ✅ 使用 `pm2 start ecosystem.config.js` 启动所有服务
3. ✅ 使用 `pm2 save` 保存配置
4. ✅ 等待3-5分钟让采集器生成数据
5. ✅ 清除浏览器缓存并强制刷新

### 如果仍然没有数据：
1. 按照"故障排查步骤"逐步检查
2. 查看日志：`pm2 logs new-high-low-collector --lines 100`
3. 检查数据文件是否存在
4. 测试API是否返回数据
5. 清除浏览器缓存

---

**文档版本**：v1.0  
**最后更新**：2026-02-28 21:05  
**系统状态**：正常运行 ✅
