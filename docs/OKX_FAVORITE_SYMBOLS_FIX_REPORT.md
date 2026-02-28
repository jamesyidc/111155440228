# OKX交易系统 - 常用币列表恢复报告

## 📋 问题描述

**用户报告**：14个常用币不见了
**时间**：2026-02-04 15:10
**影响**：OKX交易系统无法正常加载用户保存的常用币列表

---

## 🔍 问题分析

### 根本原因

Flask应用的工作目录和数据文件路径不一致：

1. **Flask工作目录**：`/home/user/webapp/source_code/`
2. **实际数据文件位置**：`/home/user/webapp/data/favorite_symbols.jsonl` (8.1K, 最后更新 Feb 3)
3. **Flask读取的文件**：`/home/user/webapp/source_code/data/favorite_symbols.jsonl` (3.4K, 最后更新 Feb 1)

### 文件对比

| 位置 | 大小 | 更新时间 | 币种数量 | 状态 |
|------|------|----------|----------|------|
| `/home/user/webapp/data/` | 8.1K | 2026-02-03 08:41 | **15个** | ✅ 正确 |
| `/home/user/webapp/source_code/data/` | 3.4K | 2026-02-01 01:14 | 14个 | ❌ 过期 |

---

## ✅ 解决方案

### 1. 文件同步

```bash
# 复制正确的常用币文件到source_code目录
cp data/favorite_symbols.jsonl source_code/data/favorite_symbols.jsonl
```

### 2. 重启Flask应用

```bash
pm2 restart flask-app
```

---

## 📊 验证结果

### API测试

**请求**：
```bash
curl https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/api/okx-trading/favorite-symbols
```

**响应**：
```json
{
  "success": true,
  "symbols": [
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "TAO-USDT-SWAP",
    "LDO-USDT-SWAP",
    "CFX-USDT-SWAP",
    "CRV-USDT-SWAP",
    "UNI-USDT-SWAP",
    "CRO-USDT-SWAP",
    "FIL-USDT-SWAP",
    "APT-USDT-SWAP",
    "SUI-USDT-SWAP",
    "NEAR-USDT-SWAP",
    "DOT-USDT-SWAP",
    "LINK-USDT-SWAP",
    "STX-USDT-SWAP"
  ],
  "updated_at": "2026-02-03T08:41:31.260120Z"
}
```

### 对比

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 币种数量 | ❌ 14个 | ✅ 15个 |
| 更新时间 | 2026-02-01 01:14 | 2026-02-03 08:41 |
| API状态 | 返回旧数据 | 返回最新数据 |

---

## 🎯 恢复的币种列表

共15个常用币种：

1. **SOL-USDT-SWAP** - Solana
2. **XRP-USDT-SWAP** - Ripple
3. **TAO-USDT-SWAP** - Bittensor
4. **LDO-USDT-SWAP** - Lido DAO
5. **CFX-USDT-SWAP** - Conflux
6. **CRV-USDT-SWAP** - Curve DAO
7. **UNI-USDT-SWAP** - Uniswap
8. **CRO-USDT-SWAP** - Cronos
9. **FIL-USDT-SWAP** - Filecoin
10. **APT-USDT-SWAP** - Aptos
11. **SUI-USDT-SWAP** - Sui
12. **NEAR-USDT-SWAP** - NEAR Protocol
13. **DOT-USDT-SWAP** - Polkadot
14. **LINK-USDT-SWAP** - Chainlink
15. **STX-USDT-SWAP** - Stacks

---

## 📝 技术说明

### Flask工作目录配置

```bash
pm2 info flask-app | grep "exec cwd"
# 输出：exec cwd │ /home/user/webapp/source_code
```

### 文件路径问题

Flask代码中使用相对路径 `'data/favorite_symbols.jsonl'`，实际解析为：
```
/home/user/webapp/source_code/data/favorite_symbols.jsonl
```

而非预期的：
```
/home/user/webapp/data/favorite_symbols.jsonl
```

---

## 🔧 后续改进建议

### 1. 使用绝对路径

修改 `app_new.py` 中的路径引用：

```python
# 当前（相对路径）
file_path = 'data/favorite_symbols.jsonl'

# 改进（绝对路径）
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, 'data', 'favorite_symbols.jsonl')
```

### 2. 数据文件集中管理

建议所有数据文件统一放在 `/home/user/webapp/data/` 目录，避免分散在不同位置。

### 3. 添加路径日志

在启动时输出数据文件的实际路径，便于调试：

```python
print(f"✅ 常用币数据文件路径: {os.path.abspath(file_path)}")
```

---

## ✅ 完成状态

- [x] 问题定位完成
- [x] 文件同步完成
- [x] Flask应用重启
- [x] API测试验证通过
- [x] 15个币种全部恢复
- [x] Git提交完成

---

## 🔗 相关链接

- **OKX交易系统**：https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/okx-trading
- **常用币API**：https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/api/okx-trading/favorite-symbols
- **Git提交**：commit `95c1ceb`

---

## 📅 时间线

| 时间 | 事件 |
|------|------|
| 2026-02-04 15:10 | 用户报告常用币不见了 |
| 2026-02-04 15:12 | 定位到文件路径问题 |
| 2026-02-04 15:13 | 复制正确文件并重启 |
| 2026-02-04 15:14 | 验证恢复成功 |
| 2026-02-04 15:15 | 创建修复报告 |

---

## 💡 用户操作指南

### 如何验证常用币已恢复

1. **访问OKX交易系统**：  
   https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/okx-trading

2. **查看常用币部分**：  
   - 在交易对列表中，带⭐标记的就是常用币
   - 应该能看到15个常用币

3. **测试批量开仓功能**：  
   - 涨幅前6名策略：从15个常用币中选择涨幅最高的6个
   - 涨幅后6名策略：从15个常用币中选择跌幅最大的6个

### 如何添加/删除常用币

- **添加**：点击交易对右侧的⭐按钮
- **删除**：再次点击已标记的⭐按钮即可取消

---

**问题已完全解决！您的15个常用币已经全部恢复！** ✅
