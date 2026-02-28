# 数据管理系统隐藏更新日志

## 📅 更新日期
2026-02-16

## 🎯 更新目标
从数据管理页面隐藏已停用的系统，只显示当前正在运行的系统，避免用户混淆。

---

## ✅ 已隐藏的系统（2个）

### 1. ⛔ 支撑压力(大盘) - 老版

**系统信息**:
- **图标**: 🎯
- **停止时间**: 2026-02-07
- **运行时长**: 41天
- **数据目录**: 
  - `support_resistance_daily/`
  - `support_resistance_jsonl/`

**数据统计**:
- 文件数: 45个
- 记录数: 1,641,238条（约164万）
- 数据大小: 1,715.78 MB（约1.72 GB）
- 日期范围: 2025-12-25 ~ 2026-02-07

**停用原因**: 
- 功能已被「价格位置预警系统 v2.0.5」完全替代
- 新系统提供更强大的功能和更高效的数据结构

**数据处理**:
- ✅ 历史数据保留（用于回测分析）
- 🔒 数据管理页面隐藏显示
- 📊 数据目录未删除，可手动访问

**替代系统**: 
📍 价格位置预警系统 v2.0.5
- URL: https://9002-xxx.sandbox.novita.ai/price-position
- 数据目录: `price_position/`, `price_speed_jsonl/`, `price_speed_10m/`

---

### 2. ⛔ 逃顶信号系统

**系统信息**:
- **图标**: 🚨
- **停止时间**: 2026-01-28
- **运行时长**: 1天
- **数据目录**: 
  - `escape_signal_jsonl/`

**数据统计**:
- 文件数: 3个
- 记录数: 56,142条（约5.6万）
- 数据大小: 11.97 MB（约12 MB）
- 日期范围: 2026-01-28

**停用原因**: 
- 功能已合并到「价格位置预警系统」
- 逃顶信号现在作为价格位置预警的一部分提供

**数据处理**:
- 🔒 数据管理页面隐藏显示
- 📊 数据目录保留（可选择删除或归档）
- ✅ 功能已整合到新系统

**合并到系统**: 
📍 价格位置预警系统 v2.0.5
- 逃顶信号作为价格位置超过95%阻力位的预警场景

---

## 🟢 当前显示的系统（7个）

数据管理页面现在只显示以下正在运行的系统：

| 序号 | 系统名称 | 图标 | 文件数 | 记录数 | 大小 | 状态 |
|------|----------|------|--------|--------|------|------|
| 1 | SAR趋势系统 | 📈 | 50 | 537,505 | 148.19 MB | ✅ 运行中 |
| 2 | OKX全生态 | 💹 | 51 | 14,249 | 26.00 MB | ✅ 运行中 |
| 3 | 27币涨跌幅追踪 | 📉 | 20 | 22,492 | 58.07 MB | ✅ 运行中 |
| 4 | 价格位置预警系统 | 📍 | 6 | 791,833 | 178.33 MB | ✅ 运行中 |
| 5 | 恐慌监控洗盘 | ⚠️ | 25 | 24,464 | 14.98 MB | 🟡 需检查 |
| 6 | 11信号日线总 | 🔔 | 10 | 2,846 | 0.59 MB | 🟡 需检查 |
| 7 | OKX日涨幅统计 | 📊 | - | - | - | ✅ 运行中 |

**总计**: 162文件，1,393,389条记录（约139万），426.16 MB

---

## 🔧 技术实现

### 修改文件列表

1. **generate_system_grouped_data.py**
   - 从 `SYSTEM_MAPPING` 中移除了「支撑压力(大盘)」
   - 从 `SYSTEM_MAPPING` 中移除了「逃顶信号系统」
   - 添加了注释说明停用原因
   - 添加了「27币涨跌幅追踪系统」

2. **ACTIVE_SYSTEMS_JSONL_DATA.md**
   - 更新活跃系统列表（7个）
   - 添加已停用系统说明（2个）
   - 更新数据统计信息

3. **data/system_grouped_data.json**
   - 重新生成，只包含活跃系统
   - 自动通过扫描脚本生成

### 代码修改对比

**修改前** (`SYSTEM_MAPPING`):
```python
"支撑压力(大盘)": {
    "dirs": ["support_resistance_jsonl", "support_resistance_daily"],
    "icon": "🎯",
    "color": "#3B82F6"
},
"逃顶信号系统": {
    "dirs": ["escape_signal_jsonl"],
    "icon": "🚨",
    "color": "#EC4899"
},
```

**修改后** (已移除，添加注释):
```python
# 注意：只显示当前正在运行的系统
# 已停用系统：支撑压力(大盘) (已被价格位置预警系统替代)
#            逃顶信号系统 (已合并到价格位置预警系统)
SYSTEM_MAPPING = {
    "SAR趋势系统": {...},
    "OKX全生态": {...},
    "27币涨跌幅追踪系统": {...},  # 新增
    "价格位置预警系统": {...},
    ...
}
```

---

## 🚀 验证步骤

### 1. 重新生成系统数据
```bash
cd /home/user/webapp
python3 generate_system_grouped_data.py
```

**预期输出**:
```
扫描系统数据...
✅ 数据已保存到: /home/user/webapp/data/system_grouped_data.json

系统统计:

📈 SAR趋势系统
  文件数: 50
  记录数: 537,505
  ...

💹 OKX全生态
  ...

（只显示7个活跃系统，不再显示支撑压力和逃顶信号）
```

### 2. 检查数据管理API
```bash
curl http://localhost:9002/api/data-management/systems-grouped | python3 -m json.tool
```

**预期结果**: 
- JSON响应中只包含7个系统
- 不包含「支撑压力(大盘)」和「逃顶信号系统」

### 3. 访问数据管理页面
```
URL: https://9002-xxx.sandbox.novita.ai/data-management
```

**预期显示**:
- ✅ 展开的系统列表中只显示7个活跃系统
- 🚫 不显示「支撑压力(大盘)」
- 🚫 不显示「逃顶信号系统」

---

## 📊 数据对比

### 隐藏前后对比

| 项目 | 隐藏前 | 隐藏后 | 变化 |
|------|--------|--------|------|
| 显示系统数 | 9个 | 7个 | -2 |
| 总文件数 | 210个 | 162个 | -48 |
| 总记录数 | 3,090,769条 | 1,393,389条 | -1,697,380 |
| 总数据量 | 2,152.11 MB | 426.16 MB | -1,725.95 MB |

**说明**: 
- 隐藏的数据实际未删除，只是不在页面显示
- 历史数据仍然保存在 `/home/user/webapp/data/` 目录中
- 可以通过直接访问目录查看历史数据

---

## 💡 用户影响

### 正面影响
1. ✅ **界面简洁**: 只显示当前运行的系统，避免混淆
2. ✅ **加载更快**: 减少需要扫描和显示的数据量
3. ✅ **数据准确**: 统计数据只包含活跃系统，更符合实际
4. ✅ **易于维护**: 新系统统一管理，减少重复功能

### 数据迁移路径
```
老版支撑压力系统 → 价格位置预警系统 v2.0.5
逃顶信号系统     → 价格位置预警系统 v2.0.5
```

### 如何访问历史数据

如果需要访问已隐藏系统的历史数据：

**方式1: 命令行直接访问**
```bash
cd /home/user/webapp/data

# 查看老版支撑压力数据
ls -lh support_resistance_daily/
ls -lh support_resistance_jsonl/

# 查看逃顶信号数据  
ls -lh escape_signal_jsonl/
```

**方式2: 临时恢复显示**
在 `generate_system_grouped_data.py` 中临时添加回系统映射，重新生成数据。

---

## 📝 Git提交记录

**Commit Hash**: `46f425b`

**Commit Message**:
```
feat: Hide deprecated systems from data management

- Removed '支撑压力(大盘)' (old support/resistance) from system mapping
- Removed '逃顶信号系统' (escape signal) from system mapping  
- Both systems have been merged into '价格位置预警系统 v2.0.5'
- Added '27币涨跌幅追踪系统' to active systems list
- Updated ACTIVE_SYSTEMS_JSONL_DATA.md documentation
- Regenerated system_grouped_data.json with only active systems

Active systems (7): SAR, OKX, 27-coin tracker, Price position, 
                    Panic monitor, 11-signal, OKX day change
Hidden systems (2): Old support/resistance (stopped 2026-02-07), 
                    Escape signal (stopped 2026-01-28)
```

**修改文件**:
```
modified:   generate_system_grouped_data.py
modified:   ACTIVE_SYSTEMS_JSONL_DATA.md
modified:   data/system_grouped_data.json
```

---

## 🔮 未来建议

### 短期建议
1. **监控系统状态**: 检查「恐慌监控洗盘」和「11信号日线总」的运行状态
2. **数据清理**: 考虑归档或删除逃顶信号系统的数据（仅占12MB）
3. **文档更新**: 在首页系统卡片上标注新旧系统替换关系

### 长期建议
1. **自动隐藏**: 添加系统状态自动检测，超过X天未更新自动隐藏
2. **归档功能**: 实现一键归档已停用系统数据到备份目录
3. **版本标记**: 为系统添加版本号，便于追踪升级历史
4. **数据迁移**: 提供历史数据格式转换工具（老格式→新格式）

---

## ❓ FAQ

### Q1: 隐藏的数据是否被删除？
**A**: 没有。数据文件仍然保存在原目录，只是不在数据管理页面显示。可以通过命令行直接访问。

### Q2: 如何恢复显示已隐藏的系统？
**A**: 编辑 `generate_system_grouped_data.py`，将系统重新添加到 `SYSTEM_MAPPING`，然后运行 `python3 generate_system_grouped_data.py`。

### Q3: 新系统包含老系统的全部功能吗？
**A**: 是的。价格位置预警系统 v2.0.5 整合了老版支撑压力系统和逃顶信号系统的所有功能，并提供了更多新特性。

### Q4: 历史数据是否需要迁移？
**A**: 不需要。历史数据保持原格式保存，用于回测分析。新数据使用新系统格式存储。

### Q5: 何时可以删除隐藏系统的数据？
**A**: 建议观察1-2个月，确认新系统稳定运行且无需历史数据对比后，再考虑删除或归档。

---

**文档创建**: 2026-02-16  
**最后更新**: 2026-02-16  
**维护人员**: AI Assistant  
**相关文档**: 
- `ACTIVE_SYSTEMS_JSONL_DATA.md`
- `SUPPORT_RESISTANCE_EXPLANATION.md`
- `PRICE_POSITION_VS_SUPPORT_RESISTANCE.md`
