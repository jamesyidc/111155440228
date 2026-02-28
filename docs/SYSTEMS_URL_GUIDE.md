# 🌐 系统访问地址导航

**生成时间**: 2026-02-07 13:10:00  
**主域名**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai

---

## 📊 主要系统访问地址

### 1. 🚨 Panic 指数监控系统
**地址**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/panic

**功能**:
- 实时恐慌指数监控
- 历史数据趋势分析
- 单位：万美元、亿美元正确显示
- panic_index 不再错误乘以 100

**状态**: ✅ 已修复，正常运行

---

### 2. 📁 Google Drive TXT 监控系统
**地址**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/gdrive-detector

**功能**:
- 实时监控 Google Drive TXT 文件
- 今日日期: 2026-02-07
- 最新文件: 2026-02-07_1023.txt
- TXT 总数: 62 个
- 数据延迟: 约 3 分钟

**API**:
- 状态: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/gdrive-detector/status
- 最新数据: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/query/latest

**状态**: ✅ 正常运行

---

### 3. 📈 支撑压力系统 v2.0 (新系统)
**监控币种**: 27个 (BTC, ETH, XRP, BNB, SOL, LTC, DOGE, SUI, TRX, TON, ETC, BCH, HBAR, XLM, FIL, LINK, CRO, DOT, AAVE, UNI, NEAR, APT, CFX, CRV, STX, LDO, TAO)

#### API 接口

**系统状态**:
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/status
```
返回: 27个币种状态、数据统计、系统信息

**最新数据** (支持单币查询):
```
# 全部币种
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/latest

# 单个币种
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/latest?inst_id=BTC-USDT-SWAP

# 多个币种
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/latest?inst_id=BTC-USDT-SWAP,ETH-USDT-SWAP
```

**历史数据** (支持时间范围):
```
# 近7天
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/history?inst_id=BTC-USDT-SWAP&days=7

# 指定时间范围
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/history?inst_id=BTC-USDT-SWAP&start_date=2026-02-01&end_date=2026-02-07
```

**交易信号**:
```
# 所有活跃信号
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/signals

# 单个币种信号
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/signals?inst_id=BTC-USDT-SWAP
```

**系统摘要**:
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/summary
```

#### 系统特性
- **数据采集**: 每60秒自动采集27个币种
- **响应速度**: API响应 <200ms
- **数据存储**: SQLite + JSONL 双重存储
- **代码规模**: 1,900行 (旧系统12,707行，减少85%)
- **内存占用**: ~32MB
- **守护进程**: PM2管理，自动重启

**状态**: ✅ 正常运行

---

### 4. 🎯 逃顶信号系统 v2.0 (新系统)
**地址**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/escape-signal-v2

**功能**:
- 按天浏览逃顶信号数据
- 左右翻页 + 日历选择
- 数据范围: 2025-12-25 ~ 2026-01-23 (30天)
- 单日记录: ~1234条
- 页面加载: <500ms (旧系统5-10秒)

#### API 接口

**可用日期列表**:
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/escape-v2/dates
```

**单日数据**:
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/escape-v2/day-data?date=2026-01-23
```

**数据摘要**:
```
https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/escape-v2/summary
```

#### 性能对比
| 指标 | 旧系统 | v2.0 | 提升 |
|------|--------|------|------|
| 页面加载 | 5-10s | <500ms | 10-20x |
| 数据传输 | ~2MB | ~10KB | 200x |
| 滚动体验 | 卡顿 | 流畅翻页 | ✅ |

**状态**: ✅ 正常运行

---

## 🔧 系统管理

### PM2 进程管理

查看所有进程:
```bash
cd /home/user/webapp && pm2 status
```

重启服务:
```bash
# 重启Flask主应用
pm2 restart flask-app

# 重启支撑压力守护进程
pm2 restart sr-v2-daemon

# 重启GDrive监控
pm2 restart gdrive-detector
```

查看日志:
```bash
# Flask日志
pm2 logs flask-app --lines 50

# 支撑压力系统日志
pm2 logs sr-v2-daemon --lines 50

# GDrive监控日志
pm2 logs gdrive-detector --lines 50
```

---

## 📦 数据存储位置

### 支撑压力系统 v2.0
- **数据库**: `/home/user/webapp/sr_v2/config/data/db/sr_v2.db`
- **JSONL**: `/home/user/webapp/sr_v2/config/data/jsonl/support_resistance.jsonl`
- **日志**: `/home/user/webapp/sr_v2/config/logs/sr_daemon.log`
- **配置**: `/home/user/webapp/sr_v2/config/config.py`

### 逃顶信号系统 v2.0
- **数据目录**: `/home/user/webapp/data/escape_signal_daily/`
- **索引文件**: `/home/user/webapp/data/escape_signal_daily/date_index.json`
- **日数据**: `/home/user/webapp/data/escape_signal_daily/escape_signal_YYYY-MM-DD.jsonl.gz`

### Google Drive TXT 监控
- **数据目录**: `/home/user/webapp/data/gdrive_jsonl/`
- **配置**: `/home/user/webapp/daily_folder_config.json`

---

## 📊 系统状态总览

| 系统 | 状态 | 运行时间 | 内存占用 |
|------|------|----------|----------|
| Flask主应用 | ✅ 在线 | 3h+ | ~140MB |
| 支撑压力v2.0 | ✅ 在线 | 持续运行 | ~32MB |
| GDrive监控 | ✅ 在线 | 2h+ | ~53MB |
| 逃顶信号v2.0 | ✅ 在线 | - | - |

---

## 🎯 27个监控币种列表

1. **BTC** - 比特币
2. **ETH** - 以太坊
3. **XRP** - Ripple
4. **BNB** - Binance Coin
5. **SOL** - Solana
6. **LTC** - 莱特币
7. **DOGE** - 狗狗币
8. **SUI** - Sui
9. **TRX** - 波场
10. **TON** - TON
11. **ETC** - 以太经典
12. **BCH** - 比特币现金
13. **HBAR** - Hedera
14. **XLM** - Stellar
15. **FIL** - Filecoin
16. **LINK** - Chainlink
17. **CRO** - Cronos
18. **DOT** - Polkadot
19. **AAVE** - Aave
20. **UNI** - Uniswap
21. **NEAR** - Near Protocol
22. **APT** - Aptos
23. **CFX** - Conflux
24. **CRV** - Curve
25. **STX** - Stacks
26. **LDO** - Lido
27. **TAO** - Bittensor

---

## 📝 快速测试命令

```bash
# 测试支撑压力系统状态
curl -s https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/status | python3 -m json.tool

# 测试BTC最新数据
curl -s https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/sr-v2/latest?inst_id=BTC-USDT-SWAP | python3 -m json.tool

# 测试逃顶信号可用日期
curl -s https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/escape-v2/dates | python3 -m json.tool

# 测试GDrive监控状态
curl -s https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/api/gdrive-detector/status | python3 -m json.tool
```

---

## 🔗 相关文档

- **支撑压力系统重构方案**: `/home/user/webapp/SUPPORT_RESISTANCE_REBUILD_PLAN.md`
- **支撑压力系统完成报告**: `/home/user/webapp/sr_v2/docs/SR_V2_COMPLETION_REPORT.md`
- **逃顶信号系统重构方案**: `/home/user/webapp/ESCAPE_SIGNAL_V2_REBUILD_PLAN.md`
- **逃顶信号系统完成报告**: `/home/user/webapp/escape_v2/docs/ESCAPE_V2_COMPLETION_REPORT.md`
- **GDrive修复报告**: `/home/user/webapp/GDRIVE_DETECTOR_FIX_REPORT.md`

---

## ⚠️ 注意事项

1. **数据更新频率**:
   - 支撑压力系统: 每60秒采集一次
   - GDrive监控: 每次检测间隔约3分钟
   - 逃顶信号: 历史数据，不实时更新

2. **API限制**:
   - 所有API响应时间 <200ms
   - 单次查询最多返回1000条记录
   - 支持GZIP压缩

3. **数据保留**:
   - SQLite数据库: 无限期
   - JSONL文件: 无限期
   - 日志文件: 最近5个备份 (10MB/文件)

---

**最后更新**: 2026-02-07 13:10:00  
**维护状态**: ✅ 所有系统正常运行
