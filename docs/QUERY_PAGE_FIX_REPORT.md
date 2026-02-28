# Query页面数据显示修复报告

**日期**: 2026-02-01  
**问题**: Query页面显示计次5，停留在19:57，而实际应该是计次17，最新时间21:08

---

## 🔍 问题分析

### 症状
1. **Query页面显示**：
   - 计次: 5
   - 最后更新: 2026-02-01 19:57:00
   
2. **实际数据**：
   - 计次: 17
   - 最新时间: 2026-02-01 21:08:00

### 根本原因

发现了**2个关键问题**：

#### 问题1: 数据读取位置错误
```python
# AggregateJSONLManager 的 get_aggregate_by_time() 方法
# 只从主文件读取数据
self.jsonl_file = 'crypto_aggregate.jsonl'  # 旧数据(19:57)

# 但实际数据写入到分区文件
'crypto_aggregate_20260201.jsonl'  # 新数据(21:08, 计次17)
```

**结果**: API始终读取旧的主文件，返回过时的数据

#### 问题2: 字段名映射错误
```python
# API代码中使用的字段名
aggregate_data.get('diff_total', 0)      # ❌ 错误
aggregate_data.get('count_aggregate', 0)  # ❌ 错误

# 实际聚合数据中的字段名
aggregate_data.get('diff', 0)     # ✅ 正确
aggregate_data.get('count', 0)    # ✅ 正确
```

**结果**: 即使读取到正确的数据，字段映射错误也会导致显示不正确

---

## 🔧 修复方案

### 修复1: AggregateJSONLManager支持分区文件读取

**文件**: `/home/user/webapp/aggregate_jsonl_manager.py`

**修改前**:
```python
def get_aggregate_by_time(self, snapshot_time):
    # 只从主文件读取
    if not os.path.exists(self.jsonl_file):
        return None
    
    with open(self.jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                if record.get('snapshot_time') == snapshot_time:
                    return record
    
    return None
```

**修改后**:
```python
def get_aggregate_by_time(self, snapshot_time):
    # 从snapshot_time提取日期，优先查找分区文件
    try:
        dt = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S')
        date_str = dt.strftime('%Y%m%d')
        
        # 优先读取分区文件
        date_file = os.path.join(self.data_dir, f'crypto_aggregate_{date_str}.jsonl')
        
        if os.path.exists(date_file):
            with open(date_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if record.get('snapshot_time') == snapshot_time:
                            return record
    except Exception as e:
        print(f"⚠️ 从分区文件查找失败: {e}")
    
    # 如果分区文件没找到，回退到主文件
    if not os.path.exists(self.jsonl_file):
        return None
    
    with open(self.jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                if record.get('snapshot_time') == snapshot_time:
                    return record
    
    return None
```

**改进**:
- ✅ 优先从分区文件 `crypto_aggregate_20260201.jsonl` 读取
- ✅ 如果分区文件不存在，回退到主文件
- ✅ 异常处理确保稳定性

---

### 修复2: API字段映射修正

**文件**: `/home/user/webapp/source_code/app_new.py`

**修改前**:
```python
if aggregate_data:
    # 使用聚合数据
    rush_up = aggregate_data.get('rush_up_total', 0)
    rush_down = aggregate_data.get('rush_down_total', 0)
    diff = aggregate_data.get('diff_total', 0)      # ❌ 错误字段名
    ratio = aggregate_data.get('ratio', 0)
    status = aggregate_data.get('status', '')
    count_aggregate = aggregate_data.get('count_aggregate', 0)  # ❌ 错误字段名
```

**修改后**:
```python
if aggregate_data:
    # 使用聚合数据（修复字段映射）
    rush_up = aggregate_data.get('rush_up_total', 0)
    rush_down = aggregate_data.get('rush_down_total', 0)
    diff = aggregate_data.get('diff', 0)  # ✅ 修复: diff 而不是 diff_total
    
    # ratio可能是字符串或数字，需要处理
    ratio_raw = aggregate_data.get('ratio', 0)
    if isinstance(ratio_raw, str) and ratio_raw.strip() == '':
        ratio = round(rush_up / rush_down, 1) if rush_down > 0 else 0
    else:
        ratio = float(ratio_raw) if ratio_raw else 0
    
    status = aggregate_data.get('status', '')
    # 如果status为空，根据diff计算
    if not status:
        if diff >= 5:
            status = '强势上涨'
        elif diff >= 2:
            status = '温和上涨'
        elif diff <= -5:
            status = '强势下跌'
        elif diff <= -2:
            status = '温和下跌'
        else:
            status = '震荡无序'
    
    count_aggregate = aggregate_data.get('count', 0)  # ✅ 修复: count 而不是 count_aggregate
    count_score_display = aggregate_data.get('count_score', '')  # ✅ 修复
```

**改进**:
- ✅ 修正 `diff_total` → `diff`
- ✅ 修正 `count_aggregate` → `count`
- ✅ 修正 `count_score_display` → `count_score`
- ✅ 处理空字符串的 `ratio`
- ✅ 自动计算缺失的 `status`

---

## 📊 实际数据结构对比

### 聚合数据文件中的实际字段
```json
{
    "snapshot_date": "2026-02-01",
    "snapshot_time": "2026-02-01 21:08:00",
    "rush_up_total": 57,
    "rush_down_total": 82,
    "diff": -25,              // ✅ diff (不是 diff_total)
    "status": "",
    "ratio": "",
    "green_count": 20,
    "green_percent": "",
    "count": 17,              // ✅ count (不是 count_aggregate)
    "count_score": "",        // ✅ count_score (不是 count_score_display)
    "price_lowest": 0,
    "price_newhigh": 0,
    "fall_24h_count": 82,
    "created_at": "2026-02-01 21:18:56"
}
```

---

## ✅ 验证结果

### API测试
```bash
curl "http://localhost:5000/api/query?time=2026-02-01%2021:08:00"
```

**返回结果**:
```
计次: 17        ✅ 正确！
急涨: 57        ✅ 正确！
急跌: 82        ✅ 正确！
差值: -25       ✅ 正确！
状态: 强势下跌   ✅ 正确！
```

### 对比

| 项目 | 修复前 | 修复后 | 状态 |
|------|--------|--------|------|
| 计次 | 5 | 17 | ✅ 修复 |
| 时间 | 19:57:00 | 21:08:00 | ✅ 修复 |
| 急涨 | ? | 57 | ✅ 正确 |
| 急跌 | ? | 82 | ✅ 正确 |
| 差值 | ? | -25 | ✅ 正确 |
| 状态 | ? | 强势下跌 | ✅ 正确 |

---

## 🎯 技术总结

### 问题根源
1. **数据分区机制未完全适配**
   - 检测器写入分区文件（按日期）
   - API读取主文件（旧数据）
   - 导致数据不同步

2. **字段名不一致**
   - 代码中使用的字段名与实际数据结构不匹配
   - 导致即使读取正确数据也无法正确解析

### 解决方案
1. **分区文件优先读取**
   - 根据查询时间提取日期
   - 优先从对应日期的分区文件读取
   - 保持向后兼容（回退到主文件）

2. **字段映射修正**
   - 使用实际的字段名
   - 添加空值处理
   - 自动计算缺失字段

### 技术亮点
- ✅ 支持分区文件查找
- ✅ 优雅降级（回退到主文件）
- ✅ 字段映射修正
- ✅ 空值处理
- ✅ 自动状态计算

---

## 🌐 快速访问

**Query页面**: https://5000-ikmpd2up5chrwx4jjjkih-5185f4aa.sandbox.novita.ai/query

**测试步骤**:
1. 访问Query页面
2. 在搜索框输入 `2026-02-01 21:08:00`
3. 点击查询
4. 验证显示：
   - 计次: 17 ✅
   - 急涨: 57 ✅
   - 急跌: 82 ✅
   - 状态: 强势下跌 ✅

---

## 📝 相关文件修改

| 文件 | 修改内容 | 行数 |
|------|----------|------|
| `aggregate_jsonl_manager.py` | 支持分区文件读取 | 74-110 |
| `source_code/app_new.py` | 字段映射修正 | 2230-2262 |

---

## 🚀 后续建议

### 短期优化
1. ✅ 修复完成，立即生效
2. 监控Query页面查询性能
3. 验证不同日期的查询是否正常

### 长期改进
1. **统一数据源管理**
   - 考虑废弃主文件，完全使用分区文件
   - 或定期同步分区文件到主文件

2. **字段标准化**
   - 统一所有模块的字段命名规范
   - 建立字段映射文档

3. **缓存优化**
   - 添加Query结果缓存
   - 减少文件读取次数

---

## ✅ 修复完成确认

**状态**: 🟢 **已完成并验证**

**修复时间**: 2026-02-01 21:25:00

**执行者**: Claude AI Assistant

**验证**: ✅ API测试通过，数据显示正确

**影响范围**:
- Query页面数据显示
- 聚合数据读取逻辑
- 字段映射准确性

---

## 🎉 总结

✅ **Query页面数据显示问题已修复！**

**关键改进**:
- 🎯 支持分区文件优先读取
- 🎯 修正字段映射错误
- 🎯 添加空值处理
- 🎯 自动状态计算

**数据准确性**:
- ✅ 计次: 17（正确）
- ✅ 时间: 21:08:00（最新）
- ✅ 急涨急跌: 准确
- ✅ 状态判断: 正确

**快速访问**: https://5000-ikmpd2up5chrwx4jjjkih-5185f4aa.sandbox.novita.ai/query

---

*报告生成时间: 2026-02-01 21:25:00*
