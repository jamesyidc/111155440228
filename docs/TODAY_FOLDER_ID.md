# Google Drive 今日文件夹ID速查

**日期**: 2026-02-01  
**文件夹ID**: `1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0`

---

## 🔗 快速访问

**Google Drive链接**:  
https://drive.google.com/drive/folders/1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0

---

## 📊 当前状态

### 监控状态
- **PM2服务**: online (PID: 710546)
- **检测间隔**: 30秒
- **文件数量**: 83个TXT文件
- **最新文件**: 2026-02-01_1343.txt
- **数据更新**: 2026-02-01 13:43:00

### 文件夹信息
```json
{
  "date": "2026-02-01",
  "folder_id": "1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0",
  "file_count": 83,
  "latest_file": "2026-02-01_1343.txt",
  "status": "正常监控中"
}
```

---

## 🛠️ 使用方法

### 1. 命令行查询

```bash
# 使用Python脚本查询
python3 /home/user/webapp/scripts/get_today_folder_id.py

# 或者从日志查找
pm2 logs gdrive-detector --nostream --lines 50 | grep "文件夹ID"
```

### 2. 在代码中使用

```python
# Python
FOLDER_ID = "1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0"
drive_url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
```

```bash
# Bash
FOLDER_ID="1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0"
echo "Today's folder: $FOLDER_ID"
```

---

## 📋 监控日志示例

```
[2026-02-01 13:58:28] ✅ 找到 2026-02-01 文件夹ID: 1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0
[2026-02-01 13:58:28] ✅ 找到 83 个TXT文件
[2026-02-01 13:58:28] 📄 最新文件: 2026-02-01_1343.txt
[2026-02-01 13:58:28] ✅ 文件未更新，无需重复导入
[2026-02-01 13:58:29] ⏳ 30秒后进行下次检测...
```

---

## 🔍 查找其他日期的文件夹ID

如需查找其他日期的文件夹ID，可以：

1. **从PM2日志查找**:
```bash
pm2 logs gdrive-detector --nostream --lines 1000 | grep "2026-01-31.*文件夹ID"
```

2. **从数据文件查找**:
```bash
# 查看最近导入的快照文件
ls -lth data/gdrive_jsonl/crypto_snapshots_*.jsonl | head -10
```

---

## 📝 说明

### 根文件夹ID（固定）
- **首页数据文件夹**: `1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV`

### 每日子文件夹ID（动态）
- 每天的数据存储在以日期命名的子文件夹中
- 文件夹名称格式: `YYYY-MM-DD`
- 监控器会自动查找当天的文件夹
- 文件夹ID会在首次检测时记录到日志

---

## ⚠️ 注意事项

### API状态显示问题
当前 `/api/gdrive-detector/status` API显示的是SQLite数据库中的旧数据。实际监控器使用JSONL文件系统，数据是最新的。

**解决方案**: API需要更新为读取JSONL数据源（待修复）

### 正确的数据源
- ✅ **JSONL文件**: `data/gdrive_jsonl/crypto_snapshots.jsonl` (最新)
- ✅ **PM2日志**: 实时监控状态
- ❌ **SQLite数据库**: 旧数据，不再使用

---

## 🎯 快速诊断

如果遇到问题，按以下顺序检查：

1. **检查PM2服务**:
```bash
pm2 status gdrive-detector
```

2. **查看最近日志**:
```bash
pm2 logs gdrive-detector --lines 30
```

3. **验证数据文件**:
```bash
ls -lth data/gdrive_jsonl/*.jsonl | head -5
tail -1 data/gdrive_jsonl/crypto_snapshots.jsonl | jq .
```

4. **测试文件夹访问**:
```bash
# 使用查询脚本
python3 scripts/get_today_folder_id.py
```

---

**最后更新**: 2026-02-01 14:00:00  
**维护者**: GenSpark AI Developer
