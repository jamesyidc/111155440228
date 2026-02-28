# 📊 数据管理与备份恢复系统

完整的JSONL数据管理、统计、备份和恢复系统。

---

## 🎯 功能特性

### 📊 数据统计功能
- ✅ 扫描所有JSONL文件（支持350+文件）
- ✅ 统计每个系统的文件数、记录数、大小
- ✅ 自动识别日期范围和天数
- ✅ 生成详细JSON统计报告
- ✅ Web界面实时查看统计数据

### 💾 备份功能
- ✅ **完整备份**：压缩tar.gz格式，包含所有数据
- ✅ **增量备份**：只备份修改过的文件，节省空间
- ✅ 自动时间戳命名
- ✅ 备份列表管理（查看、删除）
- ✅ 备份元数据记录

### 🔄 恢复功能
- ✅ 一键恢复任意备份
- ✅ 恢复前自动创建安全备份
- ✅ 支持压缩和目录格式备份恢复

---

## 📈 当前数据统计

根据最近一次扫描（2026-02-16）：

| 统计项 | 数值 |
|--------|------|
| **总目录数** | 42 个系统 |
| **总文件数** | 350 个JSONL文件 |
| **总记录数** | 3,920,525 条 |
| **总大小** | 2,798.52 MB (2.8 GB) |

### 📂 主要系统数据分布

| 系统名称 | 文件数 | 记录数 | 大小 | 日期范围 |
|---------|--------|--------|------|----------|
| support_resistance_daily | 41 | 901,992 | 976.51 MB | 2025-12-25 至 2026-02-07 (45天) |
| price_speed_jsonl | 2 | 790,864 | 172.49 MB | 2026-01-27 至 2026-02-10 (15天) |
| support_resistance_jsonl | 4 | 739,246 | 739.26 MB | 2025-12-25 至 2026-01-28 (35天) |
| v1v2_jsonl | 2 | 705,279 | 107.41 MB | 2026-01-16 至 2026-02-10 (26天) |
| sar_slope_jsonl | 3 | 412,426 | 115.68 MB | - |
| sar_jsonl | 29 | 81,491 | 20.06 MB | - |
| gdrive_jsonl | 14 | 67,245 | 34.15 MB | 2025-12-09 至 2026-02-07 (61天) |
| ... | ... | ... | ... | ... |

---

## 🚀 快速开始

### 方式1: Web界面（推荐）

访问数据管理页面：

```
https://9002-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/data-management
```

功能：
- 📊 查看数据统计概览
- 🔍 一键重新扫描数据
- 📦 创建完整备份
- 📥 创建增量备份
- 📋 查看备份列表
- 🔄 恢复备份
- 🗑️ 删除备份

### 方式2: 命令行快捷脚本

```bash
# 查看帮助
./manage_data.sh

# 扫描数据
./manage_data.sh scan

# 创建完整备份
./manage_data.sh backup

# 创建增量备份
./manage_data.sh backup-inc

# 查看备份列表
./manage_data.sh list

# 查看统计摘要
./manage_data.sh stats

# 恢复备份
./manage_data.sh restore backup_20260216_150000

# 删除备份
./manage_data.sh delete backup_20260216_150000
```

### 方式3: 直接使用Python脚本

#### 数据扫描和统计

```bash
# 运行数据管理器
python3 source_code/data_manager.py

# 查看统计报告
cat data/data_statistics.json | python3 -m json.tool
```

#### 备份管理

```bash
# 创建完整备份
python3 source_code/data_backup_service.py backup

# 创建增量备份
python3 source_code/data_backup_service.py incremental

# 列出所有备份
python3 source_code/data_backup_service.py list

# 恢复备份
python3 source_code/data_backup_service.py restore backup_20260216_150000.tar.gz

# 删除备份
python3 source_code/data_backup_service.py delete backup_20260216_150000.tar.gz
```

---

## 📡 API接口

### 数据管理API

#### 获取数据统计
```http
GET /api/data-management/statistics
```

返回示例：
```json
{
  "success": true,
  "data": {
    "scan_time": "2026-02-16 08:10:30",
    "summary": {
      "total_directories": 42,
      "total_files": 350,
      "total_records": 3920525,
      "total_size_mb": 2798.52
    },
    "directories": {
      "support_resistance_daily": {
        "files": [...],
        "total_records": 901992,
        "total_size": 1024000000,
        "date_range": {
          "min": "2025-12-25",
          "max": "2026-02-07"
        }
      },
      ...
    }
  }
}
```

#### 扫描数据目录
```http
POST /api/data-management/scan
```

### 备份管理API

#### 列出所有备份
```http
GET /api/data-backup/list
```

#### 创建备份
```http
POST /api/data-backup/create
Content-Type: application/json

{
  "type": "full"  // or "incremental"
}
```

#### 恢复备份
```http
POST /api/data-backup/restore
Content-Type: application/json

{
  "backup_name": "backup_20260216_150000.tar.gz"
}
```

#### 删除备份
```http
POST /api/data-backup/delete
Content-Type: application/json

{
  "backup_name": "backup_20260216_150000.tar.gz"
}
```

---

## 📁 文件结构

```
/home/user/webapp/
├── source_code/
│   ├── data_manager.py              # 数据扫描和统计脚本
│   └── data_backup_service.py       # 备份恢复服务脚本
├── templates/
│   └── data_management.html         # Web管理界面
├── data/
│   ├── data_statistics.json         # 统计报告
│   ├── support_resistance_daily/    # 各系统数据目录
│   ├── price_speed_jsonl/
│   ├── ...
│   └── [42个系统目录]
├── backups/                         # 备份存储目录
│   ├── backup_20260216_150000.tar.gz
│   ├── incremental_20260216_160000/
│   └── ...
├── manage_data.sh                   # 快捷命令脚本
└── DATA_MANAGEMENT_README.md        # 本文档
```

---

## 💡 使用建议

### 备份策略建议

1. **定期完整备份**：每周创建一次完整备份
2. **每日增量备份**：每天创建增量备份，节省空间
3. **保留策略**：保留最近7天的增量备份，最近4周的完整备份

### 自动化备份

可以使用cron定时任务：

```bash
# 编辑crontab
crontab -e

# 每天凌晨2点创建增量备份
0 2 * * * cd /home/user/webapp && ./manage_data.sh backup-inc >> logs/backup.log 2>&1

# 每周日凌晨3点创建完整备份
0 3 * * 0 cd /home/user/webapp && ./manage_data.sh backup >> logs/backup.log 2>&1

# 每天扫描数据并更新统计
30 1 * * * cd /home/user/webapp && ./manage_data.sh scan >> logs/scan.log 2>&1
```

---

## 🔧 高级功能

### Python集成示例

```python
from source_code.data_manager import DataManager
from source_code.data_backup_service import DataBackupService

# 数据管理
manager = DataManager(data_dir='data')
stats = manager.scan_all_data()
manager.print_summary()
manager.save_report('data/data_statistics.json')

# 备份管理
backup_service = DataBackupService(data_dir='data', backup_dir='backups')
result = backup_service.create_backup()
print(f"备份创建完成: {result['backup_file']}")

# 增量备份
incremental_result = backup_service.create_incremental_backup()
print(f"增量备份: {incremental_result['files_count']} 个文件")

# 恢复备份
restore_result = backup_service.restore_backup('backups/backup_20260216_150000.tar.gz')
```

---

## ❓ 常见问题

### Q: 扫描速度慢怎么办？
A: 扫描350个文件、392万条记录需要约1分钟。如果只需要更新统计，可以使用增量扫描。

### Q: 备份文件很大怎么办？
A: 完整备份会压缩所有数据（约2.8GB → 压缩后约800MB）。使用增量备份可以大幅减小备份大小。

### Q: 如何定期自动备份？
A: 参考"自动化备份"章节，使用cron定时任务。

### Q: 恢复备份会覆盖现有数据吗？
A: 是的，但恢复前会自动创建安全备份到 `backups/before_restore_*` 目录。

---

## 📞 技术支持

如有问题，请查看：
- Flask应用日志：`pm2 logs flask-app`
- 备份日志：`logs/backup.log`
- 扫描日志：`logs/scan.log`

---

## 📊 系统性能

- **扫描速度**：约350文件/分钟
- **备份速度**：完整备份约2-3分钟（2.8GB数据）
- **增量备份**：通常<30秒
- **恢复速度**：约1-2分钟

---

## 🎉 总结

数据管理与备份恢复系统提供了完整的数据生命周期管理能力：

✅ 数据统计和分析  
✅ 自动化备份  
✅ 一键恢复  
✅ Web界面管理  
✅ 命令行工具  
✅ API接口  

**立即开始使用**: https://9002-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/data-management
