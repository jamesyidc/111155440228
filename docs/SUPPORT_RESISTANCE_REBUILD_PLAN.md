# 支撑压力系统重构方案 v2.0

## 📋 执行摘要

**创建时间**: 2026-02-07 11:45:00  
**状态**: 📝 待实施  
**预计工期**: 1-2天  
**复杂度**: 中等  

### 核心问题
1. **代码冗余严重**: 38个文件，12,707行代码，职责重叠
2. **架构混乱**: 5个Manager类，缺乏清晰的分层
3. **维护困难**: 历史迭代多，Bug频发
4. **数据库问题**: 表结构为空或不存在

### 重构目标
构建一个**简洁、可靠、易维护**的支撑压力系统：
- 代码量减少70% (目标: ~3,800行)
- 文件数减少80% (目标: 8-10个核心文件)
- 清晰的三层架构
- 完整的测试覆盖
- 详细的文档

---

## 🏗️ 新架构设计

### 系统分层

```
┌─────────────────────────────────────────────┐
│           API层 (api_layer.py)             │
│     /api/sr/latest, /api/sr/history        │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│        业务逻辑层 (service_layer.py)        │
│  支撑压力计算、信号生成、交易决策           │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│         数据层 (data_layer.py)             │
│    数据采集、存储、查询 (JSONL + SQLite)    │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│          外部数据源 (OKX API)              │
└─────────────────────────────────────────────┘
```

### 核心模块

#### 1. 数据层 (data_layer.py) ~500行
**职责**: 数据采集、持久化、查询
```python
class SRDataManager:
    - collect_price_data(inst_ids)        # 采集价格数据
    - save_to_jsonl(records)              # 保存到JSONL
    - save_to_db(records)                 # 保存到数据库
    - query_by_time_range(start, end)     # 时间范围查询
    - get_latest_records(limit)           # 获取最新记录
```

#### 2. 业务逻辑层 (service_layer.py) ~800行
**职责**: 核心计算逻辑
```python
class SRCalculator:
    - calculate_support_resistance(prices)  # 计算支撑压力位
    - generate_trading_signals(data)        # 生成交易信号
    - analyze_trend(history)                # 趋势分析
    - risk_assessment(signal)               # 风险评估

class SRStrategy:
    - should_open_position(signal)          # 是否开仓
    - calculate_position_size(risk)         # 仓位计算
    - set_stop_loss_take_profit(price)     # 止盈止损
```

#### 3. API层 (api_layer.py) ~300行
**职责**: HTTP接口
```python
@app.route('/api/sr/latest')              # 最新数据
@app.route('/api/sr/history')             # 历史数据
@app.route('/api/sr/signals')             # 交易信号
@app.route('/api/sr/status')              # 系统状态
```

#### 4. 守护进程 (daemon.py) ~400行
**职责**: 后台采集和监控
```python
class SRDaemon:
    - collect_loop()                      # 数据采集循环
    - signal_monitoring_loop()            # 信号监控循环
    - health_check()                      # 健康检查
```

#### 5. 配置管理 (config.py) ~200行
```python
# 系统配置
SYMBOLS = ['BTC-USDT-SWAP', 'ETH-USDT-SWAP', ...]
COLLECT_INTERVAL = 60  # 秒
LOOKBACK_PERIOD = 30   # 天

# 计算参数
RESISTANCE_THRESHOLD = 0.95
SUPPORT_THRESHOLD = 1.05
MIN_TOUCH_COUNT = 3

# 交易参数
MAX_POSITION_SIZE = 1000  # USDT
RISK_PER_TRADE = 0.02     # 2%
```

#### 6. 工具库 (utils.py) ~300行
```python
def calculate_sma(prices, period)         # 移动平均
def calculate_resistance_level(prices)    # 压力位计算
def calculate_support_level(prices)       # 支撑位计算
def format_timestamp(ts)                  # 时间格式化
def send_alert(message)                   # 告警通知
```

---

## 📊 数据库设计

### 表结构

#### 1. support_resistance 表 (核心数据表)
```sql
CREATE TABLE IF NOT EXISTS support_resistance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time DATETIME NOT NULL,              -- 快照时间
    inst_id TEXT NOT NULL,                        -- 币种ID
    current_price REAL NOT NULL,                  -- 当前价格
    resistance_level REAL,                        -- 压力位
    support_level REAL,                           -- 支撑位
    resistance_distance REAL,                     -- 距离压力位
    support_distance REAL,                        -- 距离支撑位
    trend TEXT,                                   -- 趋势 (up/down/side)
    strength REAL,                                -- 强度 (0-1)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_time, inst_id)
);

CREATE INDEX idx_sr_time ON support_resistance(snapshot_time);
CREATE INDEX idx_sr_inst ON support_resistance(inst_id);
```

#### 2. trading_signals 表 (交易信号)
```sql
CREATE TABLE IF NOT EXISTS trading_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_time DATETIME NOT NULL,                -- 信号时间
    inst_id TEXT NOT NULL,                        -- 币种ID
    signal_type TEXT NOT NULL,                    -- 信号类型 (buy/sell)
    price REAL NOT NULL,                          -- 价格
    confidence REAL,                              -- 置信度 (0-1)
    risk_level TEXT,                              -- 风险等级 (low/medium/high)
    status TEXT DEFAULT 'active',                 -- 状态 (active/expired/executed)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_time ON trading_signals(signal_time);
CREATE INDEX idx_signals_status ON trading_signals(status);
```

#### 3. system_metrics 表 (系统指标)
```sql
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_time DATETIME NOT NULL,
    metric_name TEXT NOT NULL,                    -- 指标名称
    metric_value REAL,                            -- 指标值
    description TEXT,                             -- 描述
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_time ON system_metrics(metric_time);
```

---

## 🚀 实施计划

### Phase 1: 准备阶段 (2小时)
✅ **任务**:
1. 备份现有系统代码和数据
2. 创建新的目录结构
3. 设计数据库Schema
4. 编写配置文件

**交付物**:
- 备份文件: `backup/old_sr_system_20260207.tar.gz`
- 新目录: `sr_v2/`
- 数据库脚本: `sr_v2/schema.sql`

### Phase 2: 核心开发 (6-8小时)
✅ **任务**:
1. 实现数据层 (data_layer.py)
   - OKX API数据采集
   - JSONL文件读写
   - SQLite数据库操作
   
2. 实现业务逻辑层 (service_layer.py)
   - 支撑压力位计算算法
   - 趋势分析算法
   - 交易信号生成逻辑
   
3. 实现工具库 (utils.py)
   - 技术指标计算
   - 时间处理函数
   - 告警通知函数

**交付物**:
- 核心模块代码
- 单元测试用例
- 算法验证报告

### Phase 3: 接口开发 (2-3小时)
✅ **任务**:
1. API层开发 (api_layer.py)
   - RESTful API实现
   - 错误处理
   - 响应格式标准化
   
2. 守护进程开发 (daemon.py)
   - 数据采集循环
   - 信号监控
   - PM2配置

**交付物**:
- API接口文档
- 守护进程脚本
- PM2配置文件

### Phase 4: 测试验证 (3-4小时)
✅ **任务**:
1. 单元测试
2. 集成测试
3. 性能测试
4. 新旧系统对比测试

**测试指标**:
- 数据准确性: 99%+
- API响应时间: <200ms
- 系统稳定性: 24小时无故障运行

### Phase 5: 部署上线 (1-2小时)
✅ **任务**:
1. 生产环境部署
2. PM2守护进程启动
3. 监控告警配置
4. 文档整理

**交付物**:
- 部署脚本
- 运维文档
- 用户手册

---

## 📁 新目录结构

```
/home/user/webapp/sr_v2/
├── core/
│   ├── __init__.py
│   ├── data_layer.py           # 数据层 ~500行
│   ├── service_layer.py        # 业务逻辑层 ~800行
│   ├── api_layer.py            # API层 ~300行
│   └── daemon.py               # 守护进程 ~400行
├── config/
│   ├── __init__.py
│   ├── config.py               # 配置 ~200行
│   └── symbols.json            # 币种配置
├── utils/
│   ├── __init__.py
│   ├── utils.py                # 工具函数 ~300行
│   └── indicators.py           # 技术指标 ~400行
├── data/
│   ├── jsonl/                  # JSONL数据文件
│   │   ├── sr_data_20260207.jsonl
│   │   └── signals_20260207.jsonl
│   └── sr_v2.db                # SQLite数据库
├── logs/
│   └── sr_daemon.log
├── tests/
│   ├── test_data_layer.py
│   ├── test_service_layer.py
│   └── test_api_layer.py
├── docs/
│   ├── API.md                  # API文档
│   ├── ALGORITHM.md            # 算法说明
│   └── DEPLOYMENT.md           # 部署文档
├── scripts/
│   ├── init_db.py              # 数据库初始化
│   ├── migrate_data.py         # 数据迁移
│   └── backup.sh               # 备份脚本
├── schema.sql                  # 数据库Schema
├── requirements.txt            # Python依赖
├── ecosystem.config.js         # PM2配置
└── README.md                   # 系统说明
```

---

## 🎯 核心算法优化

### 1. 支撑压力位计算
**旧算法问题**: 
- 计算复杂，性能差
- 参数调优困难
- 准确率不稳定

**新算法**:
```python
def calculate_resistance_level(prices, period=30):
    """
    计算压力位
    算法: 取近期高点的加权平均
    """
    recent_highs = []
    for i in range(len(prices) - period, len(prices)):
        if i > 0 and i < len(prices) - 1:
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                recent_highs.append(prices[i])
    
    if not recent_highs:
        return None
    
    # 加权平均 (近期高点权重更大)
    weights = [1 / (len(recent_highs) - i) for i in range(len(recent_highs))]
    resistance = sum(h * w for h, w in zip(recent_highs, weights)) / sum(weights)
    
    return resistance
```

### 2. 交易信号生成
**改进点**:
- 多因子模型
- 动态阈值
- 风险评估

```python
def generate_signal(data):
    """
    生成交易信号
    综合考虑: 价格位置、趋势、成交量
    """
    price = data['current_price']
    resistance = data['resistance_level']
    support = data['support_level']
    trend = data['trend']
    
    # 计算价格位置
    price_position = (price - support) / (resistance - support)
    
    # 生成信号
    if price_position < 0.2 and trend == 'down':
        return {
            'signal': 'BUY',
            'confidence': 0.8,
            'risk': 'LOW'
        }
    elif price_position > 0.8 and trend == 'up':
        return {
            'signal': 'SELL',
            'confidence': 0.7,
            'risk': 'MEDIUM'
        }
    
    return None
```

---

## 📈 预期效果对比

| 指标 | 旧系统 | 新系统 | 改进 |
|------|--------|--------|------|
| 代码行数 | 12,707行 | ~3,800行 | ⬇️ 70% |
| 文件数量 | 38个 | 10个 | ⬇️ 74% |
| Manager类 | 5个 | 1个 | ⬇️ 80% |
| 数据库表 | 不明确 | 3个核心表 | ✅ 清晰 |
| API响应时间 | >1s | <200ms | ⬆️ 5倍 |
| 可维护性 | ⚠️ 困难 | ✅ 简单 | 显著提升 |
| 测试覆盖率 | 0% | 80%+ | 全新建立 |
| 文档完整性 | ⚠️ 缺失 | ✅ 完整 | 全面覆盖 |

---

## ⚠️ 风险评估

### 高风险
1. **数据迁移风险**
   - 问题: 旧系统数据格式可能不兼容
   - 应对: 编写迁移脚本，小批量测试
   
2. **业务中断风险**
   - 问题: 切换期间可能影响交易
   - 应对: 新旧系统并行运行2-3天

### 中风险
3. **算法准确性**
   - 问题: 新算法可能需要调优
   - 应对: 回测验证，逐步调整参数
   
4. **性能问题**
   - 问题: 大数据量可能影响性能
   - 应对: 建立索引，分批处理

### 低风险
5. **API兼容性**
   - 问题: 前端可能需要调整
   - 应对: 保持API格式一致

---

## ✅ 推进建议

### 立即行动
1. **备份现有系统** (30分钟)
   ```bash
   cd /home/user/webapp
   tar -czf backup/old_sr_system_$(date +%Y%m%d).tar.gz \
       source_code/*anchor* source_code/*support* source_code/*resistance*
   ```

2. **创建新项目结构** (30分钟)
   ```bash
   mkdir -p sr_v2/{core,config,utils,data/{jsonl,db},logs,tests,docs,scripts}
   ```

3. **开始Phase 1开发** (2小时)
   - 数据库Schema设计
   - 配置文件编写
   - 数据层框架搭建

### 关键里程碑
- **Day 1 PM**: 完成Phase 1-2 (核心功能)
- **Day 2 AM**: 完成Phase 3-4 (接口和测试)
- **Day 2 PM**: Phase 5部署上线

### 质量保证
- 每个Phase完成后进行Code Review
- 核心算法必须有单元测试
- 上线前必须通过回归测试

---

## 🎓 总结

### 为什么要重构？
1. **当前系统问题严重**: 12,707行代码，38个文件，架构混乱
2. **维护成本高**: Bug频发，修复困难
3. **扩展性差**: 添加新功能困难

### 重构价值
1. **代码量减少70%**: 从12,707行 → ~3,800行
2. **架构清晰**: 三层架构，职责明确
3. **易于维护**: 模块化设计，便于测试和修改
4. **性能提升**: API响应时间 <200ms
5. **文档完整**: API文档、算法说明、部署文档

### 投入产出比
- **投入**: 1-2天开发时间
- **产出**: 
  - 清晰可维护的代码
  - 稳定可靠的系统
  - 完整的测试和文档
  - 长期降低维护成本

---

**建议**: **立即启动重构**，新系统与旧系统并行运行2-3天验证后切换。

**下一步**: 等待你的确认，我立即开始Phase 1实施。

