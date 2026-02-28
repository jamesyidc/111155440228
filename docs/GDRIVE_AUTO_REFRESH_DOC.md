# Google Drive TXT文件自动刷新服务

## 📋 功能概述

自动刷新服务会每10分钟从Google Drive获取最新的TXT文件列表，并自动更新系统配置。

---

## 🎯 核心功能

### 1. 自动定时检查
- **检查间隔**: 600秒（10分钟）
- **首次执行**: 启动后立即执行一次
- **持续运行**: PM2守护进程保证服务稳定

### 2. 智能更新机制
- 对比文件数量是否变化
- 对比最新文件名是否变化
- 只在有变化时才更新配置
- 自动清除API缓存确保立即生效

### 3. 详细日志记录
- 带北京时间戳的操作日志
- 显示文件数量变化（+N或-N）
- 显示最新文件名
- 错误信息和异常处理

---

## 🔧 技术实现

### 文件位置
```
/home/user/webapp/
├── source_code/
│   └── auto_refresh_gdrive_txt.py    # 主程序脚本
├── ecosystem.gdrive-refresh.config.js # PM2配置
└── logs/
    ├── gdrive_txt_refresh_out.log     # 标准输出日志
    └── gdrive_txt_refresh_error.log   # 错误日志
```

### 工作流程
```
1. 从配置文件读取folder_id
   ↓
2. 访问Google Drive embeddedfolderview
   ↓
3. 正则匹配提取所有.txt文件
   ↓
4. 按文件名降序排序（最新在前）
   ↓
5. 对比是否有变化
   ↓
6. 更新配置文件
   ↓
7. 清除API缓存
   ↓
8. 等待600秒后重复
```

---

## 📊 配置更新内容

每次检测到变化时，会更新以下配置项：

```json
{
  "txt_files": ["2026-02-03_2013.txt", "2026-02-03_2003.txt", ...],
  "txt_count": 121,
  "latest_txt": "2026-02-03_2013.txt",
  "latest_txt_id": "2026-02-03_2013",
  "last_update": "2026-02-03T20:14:46+08:00",
  "update_reason": "自动刷新 - 定时获取最新TXT文件列表"
}
```

---

## 🚀 PM2管理命令

### 启动服务
```bash
pm2 start ecosystem.gdrive-refresh.config.js
```

### 查看状态
```bash
pm2 status gdrive-txt-refresh
```

### 查看日志（实时）
```bash
pm2 logs gdrive-txt-refresh
```

### 查看日志（最近50行）
```bash
pm2 logs gdrive-txt-refresh --nostream --lines 50
```

### 重启服务
```bash
pm2 restart gdrive-txt-refresh
```

### 停止服务
```bash
pm2 stop gdrive-txt-refresh
```

### 删除服务
```bash
pm2 delete gdrive-txt-refresh
```

### 查看详细信息
```bash
pm2 show gdrive-txt-refresh
```

---

## 📝 日志示例

### 正常运行日志
```
[2026-02-03 20:14:46] 🚀 Google Drive TXT文件自动刷新器启动
[2026-02-03 20:14:46] ⏱️  检查间隔: 600秒 (10分钟)
[2026-02-03 20:14:46] 📁 配置文件: /home/user/webapp/daily_folder_config.json
[2026-02-03 20:14:46] 🔄 开始更新TXT文件列表...
[2026-02-03 20:14:46] 🗑️  已清除API缓存
[2026-02-03 20:14:46] ✅ 更新成功！
[2026-02-03 20:14:46]    文件总数: 119 → 121 (+2)
[2026-02-03 20:14:46]    最新文件: 2026-02-03_2013.txt
[2026-02-03 20:14:46] 💤 等待600秒后下一次检查...
```

### 无变化日志
```
[2026-02-03 20:24:46] 🔄 开始更新TXT文件列表...
[2026-02-03 20:24:46] ✅ 文件列表无变化 (共121个文件，最新: 2026-02-03_2013.txt)
[2026-02-03 20:24:46] 💤 等待600秒后下一次检查...
```

### 错误处理日志
```
[2026-02-03 20:34:46] 🔄 开始更新TXT文件列表...
[2026-02-03 20:34:46] ❌ HTTP请求失败: 500
[2026-02-03 20:34:46] ❌ 获取文件列表失败，跳过本次更新
[2026-02-03 20:34:46] 💤 等待600秒后下一次检查...
```

---

## ⚙️ 配置说明

### 修改检查间隔
编辑 `/home/user/webapp/source_code/auto_refresh_gdrive_txt.py`:

```python
CHECK_INTERVAL = 600  # 10分钟 = 600秒

# 修改为5分钟
CHECK_INTERVAL = 300  # 5分钟 = 300秒

# 修改为15分钟
CHECK_INTERVAL = 900  # 15分钟 = 900秒
```

修改后需要重启服务：
```bash
pm2 restart gdrive-txt-refresh
```

---

## 🔍 故障排查

### 问题1：服务未运行
```bash
# 检查服务状态
pm2 status gdrive-txt-refresh

# 如果显示stopped，重新启动
pm2 restart gdrive-txt-refresh
```

### 问题2：日志显示错误
```bash
# 查看错误日志
pm2 logs gdrive-txt-refresh --err

# 或直接查看日志文件
tail -f /home/user/webapp/logs/gdrive_txt_refresh_error.log
```

### 问题3：配置文件未更新
检查以下几点：
1. 文件是否确实有变化（数量或最新文件名）
2. 配置文件权限是否正确
3. 查看日志确认更新是否成功

### 问题4：API返回旧数据
```bash
# 手动清除缓存
rm -f /tmp/gdrive_txt_files_cache.json

# 重启Flask
pm2 restart flask-app
```

---

## 📊 监控指标

### 关键指标
- **运行时长**: `pm2 status` 查看uptime
- **重启次数**: `pm2 status` 查看restart次数
- **内存占用**: 正常约5-10MB
- **CPU占用**: 检查时短暂使用，其他时间0%

### 异常告警
- 重启次数过多（>10次）
- 内存占用过高（>100MB）
- 日志中频繁出现错误
- 服务状态为stopped

---

## ✅ 验证测试

### 测试1：手动触发更新
```bash
# 停止定时服务
pm2 stop gdrive-txt-refresh

# 手动执行一次
python3 /home/user/webapp/source_code/auto_refresh_gdrive_txt.py

# 按Ctrl+C停止
# 重启定时服务
pm2 restart gdrive-txt-refresh
```

### 测试2：验证API更新
```bash
# 查看API返回的文件数量和最新文件
curl -s https://your-domain.com/api/gdrive-detector/txt-files | python3 -m json.tool | grep -E "count|files\[0\]"
```

### 测试3：检查配置文件
```bash
# 查看配置文件的最新更新时间和文件信息
cat /home/user/webapp/daily_folder_config.json | python3 -m json.tool | grep -E "txt_count|latest_txt|last_update"
```

---

## 🎉 功能优势

### 1. 自动化
- 无需手动刷新
- 无需人工干预
- 自动保持最新

### 2. 实时性
- 10分钟检查一次
- 新文件快速同步
- API数据及时更新

### 3. 可靠性
- PM2自动重启
- 错误处理机制
- 详细日志记录

### 4. 易维护
- 清晰的日志输出
- 简单的PM2命令
- 灵活的配置选项

---

## 📅 更新历史

| 版本 | 日期 | 说明 |
|-----|------|-----|
| v1.0 | 2026-02-03 | 初始版本，支持每10分钟自动刷新 |

---

## 🔗 相关文档

- [Google Drive监控系统文档](GDRIVE_DETECTOR_FIX_SUCCESS.md)
- [主副系统管理文档](SYSTEM_MANAGEMENT_COMPLETE.md)
- [PM2进程管理指南](https://pm2.keymetrics.io/)

---

**文档更新时间**: 2026-02-03 20:20:00  
**服务状态**: 🟢 正常运行  
**当前版本**: v1.0.0
