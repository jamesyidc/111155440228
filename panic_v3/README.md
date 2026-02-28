# Panic V3 - 恐慌清洗指数系统（简洁重构版）

## 🎯 设计目标

从头开始重新设计，去除旧系统的冗余bug，保持简洁高效。

## 📊 核心功能

### 1. 数据采集
- **频率**: 每1分钟采集一次
- **数据源**: https://history.btc126.com/baocang/
- **存储**: 按日期分文件存储 (panic_YYYYMMDD.jsonl)

### 2. 显示数据

#### 统计卡片
- 恐慌清洗指数 (%)
- 1小时爆仓金额 (万美元)
- 24小时爆仓金额 (万美元)
- 24小时爆仓人数 (万人)
- 全网持仓量 (亿美元)
- 最后更新时间

#### 图表1: 24小时爆仓 + 全网持仓 + 恐慌指数
- 三线图
- 标记最高点金额
- 标记所有超过1.5亿(15000万$)的点

#### 图表2: 1小时爆仓金额
- 柱状图
- 只标记一个最高点

## 📐 核心公式

```
恐慌清洗指数 = 24H爆仓人数【万人】 / 全网持仓总计【亿美元】
```

**级别划分**:
- `> 0.15` → 高恐慌
- `0.08 - 0.15` → 中等恐慌
- `< 0.08` → 低恐慌

## 📁 目录结构

```
panic_v3/
├── collector.py         # 数据采集器
├── app.py              # Flask API服务
├── migrate.py          # 数据迁移脚本
├── README.md           # 本文档
├── data/               # 数据目录
│   ├── panic_20260211.jsonl
│   ├── panic_20260210.jsonl
│   └── ...
└── templates/
    └── panic_v3.html   # 前端页面
```

## 🚀 快速开始

### 1. 迁移旧数据（可选）

如果有旧数据需要导入：

```bash
cd /home/user/webapp/panic_v3
python3 migrate.py
```

### 2. 启动采集器

```bash
cd /home/user/webapp/panic_v3
pm2 start collector.py --name panic-v3-collector --interpreter python3
```

### 3. 启动API服务

```bash
cd /home/user/webapp/panic_v3
pm2 start app.py --name panic-v3-app --interpreter python3
```

### 4. 保存PM2配置

```bash
pm2 save
```

### 5. 访问页面

浏览器打开: `http://your-domain:5001/`

## 🔌 API接口

### 获取最新数据
```bash
GET /api/latest
```

**响应**:
```json
{
  "success": true,
  "data": {
    "liquidation_1h": 3734.63,
    "liquidation_24h": 17519.77,
    "liquidation_count_24h": 7.31,
    "open_interest": 56.53,
    "panic_index": 0.1293,
    "panic_level": "中等恐慌",
    "timestamp": 1770789847000,
    "beijing_time": "2026-02-11 14:24:07"
  }
}
```

### 获取24小时历史数据
```bash
GET /api/history/24h
```

**响应**:
```json
{
  "success": true,
  "count": 1440,
  "data": [...]
}
```

### 获取指定日期数据
```bash
GET /api/history/daily?date=20260211
```

**响应**:
```json
{
  "success": true,
  "date": "20260211",
  "count": 1440,
  "data": [...]
}
```

### 获取最近N天数据
```bash
GET /api/history/recent?days=7
```

**响应**:
```json
{
  "success": true,
  "days": 7,
  "count": 10000,
  "data": [...]
}
```

## 📊 数据格式

### JSONL记录格式

```json
{
  "liquidation_1h": 3734.63,
  "liquidation_24h": 17519.77,
  "liquidation_count_24h": 7.31,
  "open_interest": 56.53,
  "panic_index": 0.1293,
  "panic_level": "中等恐慌",
  "timestamp": 1770789847000,
  "beijing_time": "2026-02-11 14:24:07"
}
```

### 字段说明

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| liquidation_1h | float | 万$ | 1小时爆仓金额 |
| liquidation_24h | float | 万$ | 24小时爆仓金额 |
| liquidation_count_24h | float | 万人 | 24小时爆仓人数 |
| open_interest | float | 亿$ | 全网持仓量 |
| panic_index | float | - | 恐慌清洗指数 |
| panic_level | string | - | 恐慌级别 |
| timestamp | int | 毫秒 | Unix时间戳 |
| beijing_time | string | - | 北京时间 |

## 🔧 数据单位转换

BTC126 API返回的原始数据需要进行单位转换：

```python
# 1小时爆仓: 美元 → 万美元
liquidation_1h = totalBlastUsd1h / 10000

# 24小时爆仓: 美元 → 万美元
liquidation_24h = totalBlastUsd24h / 10000

# 24小时爆仓人数: 人 → 万人
liquidation_count_24h = totalBlastNum24h / 10000

# 全网持仓: 原始值 → 亿美元
open_interest = amount / 100000000
```

## 🚫 数据验证规则

采集器会自动验证数据，过滤异常值：

```python
# 规则1: 爆仓人数不能超过100万人
if liquidation_count_24h > 100:
    跳过本次采集

# 规则2: 全网持仓必须在合理范围
if open_interest <= 0 or open_interest > 200:
    跳过本次采集

# 规则3: 恐慌指数必须在0-1范围内
if panic_index < 0 or panic_index > 1:
    跳过本次采集
```

## 📈 图表标记规则

### 24小时图表
- **自动标记**: 最高点（最大24h爆仓金额）
- **超过1.5亿**: 所有 `liquidation_24h > 15000` 的点都标记

### 1小时图表
- **只标记**: 一个最高点（最大1h爆仓金额）

## 🛠️ 运维命令

### 查看采集器状态
```bash
pm2 status panic-v3-collector
```

### 查看采集器日志
```bash
pm2 logs panic-v3-collector
```

### 重启采集器
```bash
pm2 restart panic-v3-collector
```

### 查看API服务状态
```bash
pm2 status panic-v3-app
```

### 查看数据文件
```bash
ls -lh /home/user/webapp/panic_v3/data/
```

### 统计数据记录数
```bash
wc -l /home/user/webapp/panic_v3/data/panic_*.jsonl
```

## 🐛 故障排查

### 采集器不工作

1. 检查进程状态
```bash
pm2 status panic-v3-collector
```

2. 查看错误日志
```bash
pm2 logs panic-v3-collector --lines 50
```

3. 手动测试采集
```bash
cd /home/user/webapp/panic_v3
python3 collector.py
# Ctrl+C 停止
```

### API返回空数据

1. 检查数据文件
```bash
ls -lh data/
tail -1 data/panic_$(date +%Y%m%d).jsonl
```

2. 检查Flask日志
```bash
pm2 logs panic-v3-app --lines 50
```

3. 测试API
```bash
curl -s http://localhost:5001/api/latest | python3 -m json.tool
```

### 前端不显示

1. 清除浏览器缓存
2. 检查浏览器控制台
3. 验证API是否正常
4. 检查端口是否正确(5001)

## ✨ 与旧系统对比

| 特性 | 旧系统 | V3系统 |
|------|--------|---------|
| 采集频率 | 5分钟 | 1分钟 |
| 数据存储 | 单文件 | 按日分文件 |
| 代码复杂度 | 高 | 低 |
| 兼容性 | 支持旧格式 | 简洁新格式 |
| 数据迁移 | - | 提供迁移脚本 |
| 端口 | 5000 | 5001 |

## 📝 注意事项

1. **端口**: V3系统使用5001端口，避免与旧系统冲突
2. **数据独立**: V3的数据存储在独立目录，不影响旧系统
3. **可并行运行**: V3可以与旧系统同时运行
4. **逐步迁移**: 建议先测试V3，稳定后再停用旧系统

## 📞 技术支持

如有问题，请参考：
1. 本README文档
2. 代码注释
3. PM2日志
4. Git提交历史

---

**版本**: V3.0  
**创建时间**: 2026-02-11  
**状态**: 生产就绪
