# 📊 数据管理与备份系统使用指南

## 系统概览

本系统提供了完整的JSONL数据管理和备份恢复功能，支持350个文件、392万条记录、2.8GB数据的管理。

### 📈 数据统计（截至最后扫描）

| 统计项 | 数量 |
|--------|------|
| **总目录数** | 42 个 |
| **总文件数** | 350 个 |
| **总记录数** | 3,920,525 条 |
| **总大小** | 2,798.52 MB |

---

## 🗂️ 各系统数据详情（TOP 10）

### 1. 📁 support_resistance_daily
- **文件数**: 41 个
- **记录数**: 901,992 条
- **大小**: 976.51 MB
- **日期范围**: 2025-12-25 至 2026-02-07 (45 天)
- **说明**: 支撑阻力位日线数据

### 2. 📁 price_speed_jsonl
- **文件数**: 2 个
- **记录数**: 790,864 条
- **大小**: 172.49 MB
- **日期范围**: 2026-01-27 至 2026-02-10 (15 天)
- **说明**: 价格速度数据

### 3. 📁 support_resistance_jsonl
- **文件数**: 4 个
- **记录数**: 739,246 条
- **大小**: 739.26 MB
- **日期范围**: 2025-12-25 至 2026-01-28 (35 天)
- **说明**: 支撑阻力位数据

### 4. 📁 v1v2_jsonl
- **文件数**: 2 个
- **记录数**: 705,279 条
- **大小**: 107.41 MB
- **日期范围**: 2026-01-16 至 2026-02-10 (26 天)
- **说明**: V1V2版本数据

### 5. 📁 sar_slope_jsonl
- **文件数**: 3 个
- **记录数**: 412,426 条
- **大小**: 115.68 MB
- **说明**: SAR斜率数据

### 6. 📁 sar_jsonl
- **文件数**: 29 个
- **记录数**: 81,491 条
- **大小**: 20.06 MB
- **说明**: SAR指标数据（按币种）

### 7. 📁 gdrive_jsonl
- **文件数**: 14 个
- **记录数**: 67,245 条
- **大小**: 34.15 MB
- **日期范围**: 2025-12-09 至 2026-02-07 (61 天)
- **说明**: Google Drive同步数据

### 8. 📁 escape_signal_jsonl
- **文件数**: 3 个
- **记录数**: 56,142 条
- **大小**: 11.97 MB
- **日期范围**: 2026-01-06 至 2026-02-07 (33 天)
- **说明**: 逃顶信号数据

### 9. 📁 sar_1min
- **文件数**: 2 个
- **记录数**: 30,878 条
- **大小**: 5.69 MB
- **日期范围**: 2026-02-01 至 2026-02-02 (2 天)
- **说明**: SAR 1分钟数据

### 10. 📁 anchor_profit_stats
- **文件数**: 1 个
- **记录数**: 23,411 条
- **大小**: 162.14 MB
- **说明**: 锚定利润统计

---

## 🌐 Web界面使用

### 访问地址
```
http://localhost:9002/data-management
或
https://9002-xxx.sandbox.novita.ai/data-management
```

### 功能模块

#### 1. 数据统计概览
显示实时统计信息：
- 总目录数
- 总文件数
- 总记录数
- 总大小

**操作**：点击"🔍 重新扫描数据"按钮更新统计

#### 2. 备份管理
- **创建完整备份**：打包所有数据为 `.tar.gz` 文件
- **创建增量备份**：只备份修改过的文件
- **备份列表**：显示所有已创建的备份

#### 3. 各系统数据详情
按记录数降序显示每个系统的详细信息：
- 文件数量
- 记录总数
- 数据大小
- 日期范围

---

## 💻 命令行使用

### 1. 数据统计扫描

```bash
# 扫描所有数据并生成统计报告
cd /home/user/webapp
python3 source_code/data_manager.py

# 查看统计报告
cat data/data_statistics.json
```

### 2. 备份操作

#### 创建完整备份
```bash
python3 source_code/data_backup_service.py backup
```
- 输出文件：`backups/backup_YYYYMMDD_HHMMSS.tar.gz`
- 压缩后大小约：800-1000 MB

#### 创建增量备份
```bash
python3 source_code/data_backup_service.py incremental
```
- 只备份修改过的文件
- 速度更快，占用空间小

#### 列出所有备份
```bash
python3 source_code/data_backup_service.py list
```

#### 恢复备份
```bash
# 恢复指定备份
python3 source_code/data_backup_service.py restore backup_20260216_120000.tar.gz

# 恢复前会自动创建安全备份
```

#### 删除备份
```bash
python3 source_code/data_backup_service.py delete backup_20260216_120000.tar.gz
```

---

## 🔧 API接口

### 1. 获取统计信息
```http
GET /api/data-management/statistics
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "scan_time": "2026-02-16 08:00:00",
    "summary": {
      "total_directories": 42,
      "total_files": 350,
      "total_records": 3920525,
      "total_size_mb": 2798.52
    },
    "directories": { ... }
  }
}
```

### 2. 扫描数据
```http
POST /api/data-management/scan
```

**响应**：返回扫描后的统计数据

### 3. 创建备份
```http
POST /api/data-backup/create
Content-Type: application/json

{
  "type": "full"  // 或 "incremental"
}
```

**响应示例**：
```json
{
  "success": true,
  "message": "备份创建成功",
  "output": "✅ 备份完成！大小: 950.23 MB"
}
```

### 4. 列出备份
```http
GET /api/data-backup/list
```

### 5. 恢复备份
```http
POST /api/data-backup/restore
Content-Type: application/json

{
  "backup_name": "backup_20260216_120000.tar.gz"
}
```

### 6. 删除备份
```http
POST /api/data-backup/delete
Content-Type: application/json

{
  "backup_name": "backup_20260216_120000.tar.gz"
}
```

---

## 📋 备份策略建议

### 日常备份策略

1. **每日完整备份**（推荐）
   ```bash
   # 添加到cron任务
   0 2 * * * cd /home/user/webapp && python3 source_code/data_backup_service.py backup
   ```

2. **每小时增量备份**（可选）
   ```bash
   # 添加到cron任务
   0 * * * * cd /home/user/webapp && python3 source_code/data_backup_service.py incremental
   ```

3. **保留策略**
   - 完整备份：保留最近7天
   - 增量备份：保留最近24小时
   - 每周备份：保留最近4周
   - 每月备份：保留最近12个月

---

## 🔒 数据安全

### 备份前检查
- ✅ 确保磁盘空间充足（至少3GB可用空间）
- ✅ 确认数据采集服务正常运行
- ✅ 检查最近的数据是否完整

### 恢复前注意
- ⚠️ 系统会自动创建安全备份
- ⚠️ 恢复操作不可撤销
- ⚠️ 建议在低峰期进行恢复

### 备份验证
```bash
# 检查备份文件完整性
tar -tzf backups/backup_20260216_120000.tar.gz | head -20

# 查看备份大小
du -sh backups/*.tar.gz
```

---

## 🚨 故障排除

### 问题1：扫描速度慢
**原因**：数据量大（392万条记录）
**解决**：扫描需要30-60秒，请耐心等待

### 问题2：备份失败
**原因**：磁盘空间不足
**解决**：
```bash
# 检查磁盘空间
df -h

# 清理旧备份
python3 source_code/data_backup_service.py list
python3 source_code/data_backup_service.py delete <old_backup_name>
```

### 问题3：API超时
**原因**：操作耗时较长
**解决**：增加API超时时间（已设置为600秒）

---

## 📞 技术支持

如有问题，请查看：
1. Flask日志：`logs/flask-app-out.log`
2. 数据统计报告：`data/data_statistics.json`
3. PM2服务状态：`pm2 status`

---

## 📝 更新日志

### v1.0.0 (2026-02-16)
- ✅ 初始版本发布
- ✅ 支持350个文件的统计管理
- ✅ 支持完整备份和增量备份
- ✅ Web管理界面上线
- ✅ API接口完善
