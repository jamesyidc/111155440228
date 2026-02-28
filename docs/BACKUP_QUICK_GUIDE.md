# 🚀 WebApp 系统备份快速使用指南

## 📦 备份文件信息

**备份文件**: `/tmp/webapp-backup-20260207_002930.tar.gz`  
**文件大小**: 217 MB  
**MD5 校验**: `bf47788ff7604293e2924a6de2f1809a`  
**创建时间**: 2026-02-07 00:29:30

---

## ⚡ 快速操作

### 1️⃣ 下载备份到本地

```bash
# 从服务器下载备份文件
scp user@server:/tmp/webapp-backup-20260207_002930.tar.gz ~/Downloads/

# 同时下载 MD5 文件
scp user@server:/tmp/webapp-backup-20260207_002930.tar.gz.md5 ~/Downloads/
```

### 2️⃣ 验证备份完整性

```bash
cd ~/Downloads
md5sum -c webapp-backup-20260207_002930.tar.gz.md5
# 输出: webapp-backup-20260207_002930.tar.gz: OK
```

### 3️⃣ 快速恢复（在新服务器上）

```bash
# 1. 解压备份
cd /tmp
tar -xzf webapp-backup-20260207_002930.tar.gz

# 2. 恢复代码
mkdir -p /home/user/webapp
cd /home/user/webapp
tar -xzf /tmp/webapp-backup-20260207_002930/code/python-code.tar.gz
tar -xzf /tmp/webapp-backup-20260207_002930/code/templates-static.tar.gz

# 3. 恢复配置
tar -xzf /tmp/webapp-backup-20260207_002930/configs/app-configs.tar.gz

# 4. 恢复数据
tar -xzf /tmp/webapp-backup-20260207_002930/data/databases.tar.gz
tar -xzf /tmp/webapp-backup-20260207_002930/data/recent-data-3days.tar.gz

# 5. 安装依赖
pip3 install -r /tmp/webapp-backup-20260207_002930/system/requirements.txt

# 6. 恢复 PM2 进程
cp /tmp/webapp-backup-20260207_002930/pm2/dump.pm2 ~/.pm2/
pm2 resurrect

# 7. 验证
pm2 list
curl http://localhost:5000/
```

---

## 📚 详细文档

### 完整恢复指南
查看 **`DEPLOYMENT_RESTORE_GUIDE.md`** 获取：
- ✅ 系统要求和前置条件
- ✅ 详细的 8 步恢复流程
- ✅ PM2 进程管理说明
- ✅ 配置文件详解
- ✅ 故障排查指南
- ✅ 定期维护建议

### 备份报告
查看 **`BACKUP_COMPLETE_REPORT.md`** 了解：
- ✅ 备份内容详细清单
- ✅ PM2 进程列表（23 个）
- ✅ Python 依赖列表（191 个包）
- ✅ 备份文件结构说明
- ✅ 验证结果和统计信息

---

## 🔄 定期备份

### 手动创建新备份

```bash
cd /home/user/webapp
bash create_deployment_backup.sh
```

### 自动化备份（推荐）

```bash
# 添加到 crontab（每天凌晨 2 点备份）
crontab -e

# 添加以下行：
0 2 * * * cd /home/user/webapp && bash create_deployment_backup.sh && find /tmp -name "webapp-backup-*.tar.gz" -mtime +7 -delete
```

---

## 📊 备份内容摘要

| 类别 | 内容 | 大小 |
|------|------|------|
| **代码** | Python 文件 (88) + HTML 模板 (88) | 9.9 MB |
| **配置** | JSON/YAML 配置文件 | 17 KB |
| **数据** | 数据库 + 最近3天数据 | 212 MB |
| **PM2** | 23 个进程配置 | 241 KB |
| **系统** | Python/Node 依赖信息 | 12 KB |
| **文档** | 440+ Markdown 文档 | 若干 KB |
| **总计** | 完整系统备份 | **217 MB** |

---

## 🔐 安全提示

⚠️  **备份包含敏感信息**，请：
- 🔒 使用加密传输（SSH/SCP）
- 🔒 限制文件权限：`chmod 600 backup.tar.gz`
- 🔒 考虑加密备份：`gpg --symmetric backup.tar.gz`
- 🔒 定期清理旧备份

---

## 📞 支持联系

**文档位置**:
- 📄 完整恢复指南: `/home/user/webapp/DEPLOYMENT_RESTORE_GUIDE.md`
- 📄 备份报告: `/home/user/webapp/BACKUP_COMPLETE_REPORT.md`
- 📄 备份脚本: `/home/user/webapp/create_deployment_backup.sh`

**系统访问**:
- 🌐 主页: `http://your-server:5000/`
- 🌐 重大事件监控: `http://your-server:5000/major-events`
- 🌐 数据健康监控: `http://your-server:5000/data-health-monitor`

---

## ✅ 检查清单

部署前请确认：
- [ ] 备份文件已下载到安全位置
- [ ] MD5 校验通过
- [ ] 目标服务器满足系统要求
- [ ] Python 3.8+ 和 Node.js 16+ 已安装
- [ ] PM2 已全局安装
- [ ] 必要的端口（5000）未被占用

---

**创建时间**: 2026-02-07  
**备份版本**: 1.0  
**维护者**: WebApp Team

---

## 🎯 核心命令速查

```bash
# 验证备份
md5sum -c webapp-backup-*.tar.gz.md5

# 查看备份内容
tar -tzf webapp-backup-*.tar.gz

# 解压特定文件
tar -xzf webapp-backup-*.tar.gz [path/to/file]

# 创建新备份
bash create_deployment_backup.sh

# 恢复 PM2 进程
pm2 resurrect

# 查看进程状态
pm2 list
pm2 logs flask-app
```

---

💡 **提示**: 建议每周创建一次备份，并保留最近 3 个备份文件。
