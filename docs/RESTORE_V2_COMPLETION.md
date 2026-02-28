# 安全恢复流程V2 - 完成报告

## 🎯 需求回顾

根据您的要求，实现了一个更安全的恢复流程：

### ❌ 旧流程的问题
- 直接恢复到系统目录（不安全）
- 没有数据对比环节
- 没有人工确认环节

### ✅ 新流程的改进
1. **解压到staging区**（临时恢复区，不影响系统）
2. **数据对比**（生成详细的差异报告）
3. **人工确认**（必须经过用户同意才能应用）
4. **自动快照+回滚**（应用前自动备份，出错可回滚）

---

## 🔄 新的恢复流程（4步骤）

### Step 1: 解压到Staging区
```
API: POST /api/data-sync/restore/extract
参数: { "backup_file": "sender_backup_xxx.tar.gz" }

功能：
- 解压备份到临时staging目录
- 创建恢复会话（session_id）
- 不影响系统运行数据
- 扫描所有待恢复的文件

返回：
{
  "success": true,
  "session_id": "20260204_091500",
  "staging_dir": "/path/to/staging/20260204_091500",
  "file_count": 50,
  "staging_files": ["data/xxx.jsonl", ...],
  "metadata": {...}
}
```

### Step 2: 数据对比
```
API: POST /api/data-sync/restore/compare
参数: { "session_id": "20260204_091500" }

功能：
- 加载staging区的数据（JSONL）
- 加载系统当前的数据（JSONL）
- 逐文件、逐记录对比
- 生成详细的差异报告

返回：
{
  "success": true,
  "session_id": "20260204_091500",
  "summary": {
    "total_files": 50,
    "total_differences": 120,
    "files_with_differences": 15,
    "total_added": 30,      // 新增记录数
    "total_removed": 20,    // 删除记录数
    "total_modified": 70,   // 修改记录数
    "total_unchanged": 1000 // 未变化记录数
  },
  "details": [
    {
      "staging_file": "data/coin_price_jsonl/latest_price.jsonl",
      "system_file": "coin_price_jsonl/latest_price.jsonl",
      "system_exists": true,
      "staging_count": 100,
      "system_count": 90,
      "added_records": 10,
      "removed_records": 0,
      "modified_records": 5,
      "unchanged_records": 85,
      "differences_preview": [
        {
          "index": 0,
          "type": "added",
          "staging": {"symbol": "BTC", "price": 50000},
          "system": null
        },
        ...
      ]
    },
    ...
  ]
}
```

### Step 3: 人工确认后应用
```
API: POST /api/data-sync/restore/apply
参数: { 
  "session_id": "20260204_091500",
  "user_confirmed": true  // 必须为true
}

流程：
1. 检查用户是否已确认
2. 创建系统快照备份（用于回滚）
3. 从staging复制数据到系统目录
4. 记录应用结果

返回：
{
  "success": true,
  "session_id": "20260204_091500",
  "files_copied": 50,
  "files_failed": 0,
  "copied_files": ["data/xxx.jsonl", ...],
  "snapshot_backup": "rollback_snapshot_20260204_091530.tar.gz",
  "can_rollback": true
}
```

### Step 4: 回滚（如果出错）
```
API: POST /api/data-sync/restore/rollback
参数: { "session_id": "20260204_091500" }

功能：
- 使用Step 3创建的快照
- 恢复到应用前的状态
- 删除错误的数据

返回：
{
  "success": true,
  "session_id": "20260204_091500",
  "snapshot_file": "rollback_snapshot_20260204_091530.tar.gz",
  "message": "已成功回滚到恢复前状态"
}
```

---

## 📁 目录结构

### Staging区域
```
webapp/
└── restore_staging/           # 恢复临时区域
    └── 20260204_091500/       # 会话ID目录
        ├── metadata.json      # 备份元数据
        └── data/              # 备份数据
            ├── coin_price_jsonl/
            │   └── latest_price.jsonl
            ├── sar_jsonl/
            │   └── BTC.jsonl
            └── ...
```

### 快照备份
```
webapp/
└── backups/
    └── snapshots/
        └── rollback_snapshot_20260204_091530.tar.gz  # 回滚快照
```

### 会话数据
```
webapp/
└── data/
    └── restore_sessions.json  # 所有恢复会话记录
```

---

## 🔐 安全特性

### 1. 数据隔离
- ✅ Staging区完全独立
- ✅ 不影响系统运行
- ✅ 可随时取消

### 2. 详细对比
- ✅ 逐文件对比
- ✅ 逐记录对比
- ✅ 显示增删改统计
- ✅ 差异预览（前10条）

### 3. 人工确认
- ✅ 必须`user_confirmed=true`才能应用
- ✅ 前端需要用户点击确认按钮
- ✅ 可以查看完整差异后再决定

### 4. 快照+回滚
- ✅ 应用前自动创建快照
- ✅ 快照文件独立存储
- ✅ 回滚功能完整
- ✅ 可多次回滚

### 5. 会话管理
- ✅ 每次恢复创建独立会话
- ✅ 记录完整状态（staged → compared → applied → rolled_back）
- ✅ 可查询会话历史
- ✅ 可取消未完成的会话

---

## 📊 API端点总览

| API | 方法 | 功能 | 需要确认 |
|-----|------|------|---------|
| `/api/data-sync/restore/extract` | POST | 解压到staging | ❌ |
| `/api/data-sync/restore/compare` | POST | 对比数据 | ❌ |
| `/api/data-sync/restore/apply` | POST | 应用恢复 | ✅ 需要 |
| `/api/data-sync/restore/rollback` | POST | 回滚恢复 | ❌ |
| `/api/data-sync/restore/session/<id>` | GET | 获取会话详情 | ❌ |
| `/api/data-sync/restore/sessions` | GET | 列出所有会话 | ❌ |
| `/api/data-sync/restore/session/<id>/cancel` | POST | 取消会话 | ❌ |

---

## 🎨 前端交互流程

### 用户操作流程
```
1. 选择备份文件
   ↓
2. 点击"开始恢复"
   → 调用 /restore/extract
   → 显示"正在解压..."
   ↓
3. 自动对比数据
   → 调用 /restore/compare
   → 显示差异报告
   ↓
4. 用户查看差异
   → 显示：
     - 将新增 30 条记录
     - 将删除 20 条记录
     - 将修改 70 条记录
     - 共影响 15 个文件
   → 显示前10条差异详情
   ↓
5. 用户确认
   → 用户点击"确认恢复"按钮
   → 调用 /restore/apply (user_confirmed=true)
   → 显示"正在应用..."
   ↓
6. 恢复完成
   → 显示：
     - ✅ 恢复成功
     - 已复制 50 个文件
     - 快照备份: rollback_xxx.tar.gz
     - 可以回滚
   ↓
7. (可选) 如果发现问题
   → 点击"回滚"按钮
   → 调用 /restore/rollback
   → 恢复到之前状态
```

---

## 💻 代码实现

### 核心文件
- **restore_manager_v2.py** (582行)
  - `RestoreManagerV2` 类
  - `extract_to_staging()` - Step 1
  - `compare_staging_with_system()` - Step 2
  - `apply_restore_with_confirmation()` - Step 3
  - `rollback_restore()` - Step 4
  - 会话管理方法

### 数据对比逻辑
```python
def _compare_jsonl_data(self, staging_data, system_data):
    """对比两组JSONL数据"""
    comparison = {
        'staging_count': len(staging_data),
        'system_count': len(system_data),
        'added_records': 0,
        'removed_records': 0,
        'modified_records': 0,
        'unchanged_records': 0,
        'differences': []
    }
    
    # 逐条对比
    for i in range(max(len(staging_data), len(system_data))):
        staging_item = staging_data[i] if i < len(staging_data) else None
        system_item = system_data[i] if i < len(system_data) else None
        
        if staging_item and not system_item:
            comparison['added_records'] += 1
            # 记录差异...
        elif not staging_item and system_item:
            comparison['removed_records'] += 1
            # 记录差异...
        elif staging_item != system_item:
            comparison['modified_records'] += 1
            # 记录差异...
        else:
            comparison['unchanged_records'] += 1
    
    return comparison
```

---

## 📋 会话状态机

```
staged (已解压)
  ↓ compare
compared (已对比)
  ↓ apply (with user_confirmed=true)
applied (已应用) ←→ rolled_back (已回滚)
  ↓ rollback
```

---

## 🧪 使用示例

### 完整恢复流程（Python）
```python
import requests

# Step 1: 解压
response = requests.post('http://localhost:5000/api/data-sync/restore/extract', json={
    'backup_file': 'sender_backup_20260204_090000.tar.gz'
})
session_id = response.json()['session_id']
print(f"会话ID: {session_id}")

# Step 2: 对比
response = requests.post('http://localhost:5000/api/data-sync/restore/compare', json={
    'session_id': session_id
})
comparison = response.json()
print(f"差异总数: {comparison['summary']['total_differences']}")
print(f"新增: {comparison['summary']['total_added']}")
print(f"删除: {comparison['summary']['total_removed']}")
print(f"修改: {comparison['summary']['total_modified']}")

# Step 3: 人工确认
confirm = input("是否确认恢复? (yes/no): ")
if confirm.lower() == 'yes':
    response = requests.post('http://localhost:5000/api/data-sync/restore/apply', json={
        'session_id': session_id,
        'user_confirmed': True
    })
    result = response.json()
    print(f"恢复成功! 快照: {result['snapshot_backup']}")
    
    # Step 4: (可选) 如果发现问题，回滚
    rollback = input("是否回滚? (yes/no): ")
    if rollback.lower() == 'yes':
        response = requests.post('http://localhost:5000/api/data-sync/restore/rollback', json={
            'session_id': session_id
        })
        print("已回滚!")
```

---

## 🎯 与旧系统的对比

| 特性 | 旧系统 | 新系统V2 |
|------|--------|----------|
| 恢复方式 | 直接覆盖 | 先staging后确认 |
| 数据对比 | ❌ 无 | ✅ 详细对比 |
| 人工确认 | ❌ 无 | ✅ 必须确认 |
| 回滚功能 | ❌ 无 | ✅ 完整回滚 |
| 安全性 | ⚠️ 中 | ✅ 高 |
| 会话管理 | ❌ 无 | ✅ 完整管理 |

---

## 🚀 下一步工作

### 前端界面更新（待实现）
需要更新前端的恢复操作界面：

1. **恢复按钮点击** → 不再直接恢复，而是：
   - 调用 `/restore/extract`
   - 显示"正在解压..."
   
2. **显示差异报告界面**：
   ```html
   <div class="comparison-report">
     <h3>📊 数据差异报告</h3>
     <div class="summary">
       <div>总文件数: 50</div>
       <div>有差异文件: 15</div>
       <div style="color: green">新增记录: 30</div>
       <div style="color: red">删除记录: 20</div>
       <div style="color: orange">修改记录: 70</div>
       <div>未变化记录: 1000</div>
     </div>
     
     <div class="differences">
       <h4>差异详情（前10条）</h4>
       <!-- 显示差异预览 -->
     </div>
     
     <div class="actions">
       <button onclick="confirmRestore()">✅ 确认恢复</button>
       <button onclick="cancelRestore()">❌ 取消</button>
     </div>
   </div>
   ```

3. **确认后应用**：
   - 用户点击"确认恢复"
   - 调用 `/restore/apply` (user_confirmed=true)
   - 显示进度和结果

4. **回滚按钮**：
   - 恢复后显示"回滚"按钮
   - 点击后调用 `/restore/rollback`

---

## ✅ 完成状态

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| 后端代码 | ✅ | restore_manager_v2.py |
| API端点 | ✅ | 7个新端点 |
| 数据对比 | ✅ | 完整实现 |
| 人工确认 | ✅ | 需要user_confirmed=true |
| 回滚功能 | ✅ | 完整实现 |
| 会话管理 | ✅ | 完整实现 |
| 前端界面 | ⏳ | 待更新 |

---

## 📝 总结

已成功实现了您要求的安全恢复流程：

✅ **不直接恢复到系统** - 使用staging区域  
✅ **数据对比** - 详细的差异报告  
✅ **人工确认** - 必须用户同意  
✅ **防错机制** - 自动快照+回滚

这是一个生产级别的安全恢复系统，完全符合您的需求！

---

**文档版本**: V2.0  
**完成日期**: 2026-02-04  
**开发者**: Claude Code Assistant
