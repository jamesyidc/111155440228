# 数据同步快速参考

## 一、快速开始

### 从旧系统导出数据
```bash
node scripts/export_daily_data.js <旧系统URL> [输出文件]
```

示例:
```bash
# 使用默认文件名
node scripts/export_daily_data.js https://9002-it9wfu5ka4bz8qx2ukowr-b32ec7bb.sandbox.novita.ai

# 指定文件名
node scripts/export_daily_data.js https://9002-it9wfu5ka4bz8qx2ukowr-b32ec7bb.sandbox.novita.ai backup_20260224.json
```

### 导入数据到新系统
```bash
node scripts/import_daily_data.js <新系统URL> <数据文件>
```

示例:
```bash
node scripts/import_daily_data.js https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai backup_20260224.json
```

## 二、API直接调用

### 导出数据 (GET)
```bash
curl -o backup.json http://localhost:9002/api/data-sync/export
```

### 导入数据 (POST)
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @backup.json \
  http://localhost:9002/api/data-sync/import
```

## 三、常用命令

### 查看导出的数据文件
```bash
cat backup.json | jq '.total_files, .total_size_mb'
cat backup.json | jq '.files[].path'
```

### 验证导入结果
```bash
# 检查文件是否存在
ls -lh data/coin_alert_settings/settings.jsonl

# 查看文件行数
wc -l data/coin_alert_settings/settings.jsonl

# 查看备份文件
ls -lh data/*/*.backup_*
```

### 恢复备份
```bash
# 查找备份
find data/ -name "*.backup_*"

# 恢复单个文件
cp data/coin_alert_settings/settings.jsonl.backup_20260224_120137 \
   data/coin_alert_settings/settings.jsonl
```

## 四、故障排查

### 检查系统状态
```bash
# 检查Flask应用
pm2 status flask-app
curl http://localhost:9002/health

# 重启Flask
pm2 restart flask-app
```

### 检查数据完整性
```bash
# 验证JSON格式
python3 -m json.tool < backup.json > /dev/null

# 查看文件大小
du -sh backup.json

# 查看文件内容
head -20 backup.json
```

### 网络测试
```bash
# 测试连接
curl -I https://9002-xxx.sandbox.novita.ai

# 测试API
curl https://9002-xxx.sandbox.novita.ai/api/data-sync/export | jq '.success'
```

## 五、关键文件路径

### 脚本位置
- 导出脚本: `/home/user/webapp/scripts/export_daily_data.js`
- 导入脚本: `/home/user/webapp/scripts/import_daily_data.js`

### 数据目录
- 主数据: `/home/user/webapp/data/`
- 币种设置: `data/coin_alert_settings/`
- OKX设置: `data/okx_tpsl_settings/`
- 每日数据: `data/coin_change_tracker/`

### 文档位置
- 完整文档: `/home/user/webapp/DATA_SYNC_GUIDE.md`
- 快速参考: `/home/user/webapp/DATA_SYNC_QUICK_REF.md`

## 六、注意事项

1. **交易日逻辑**: 00:00-02:00算作前一天
2. **自动备份**: 导入前自动备份原文件
3. **文件覆盖**: 导入会覆盖现有文件（但有备份）
4. **网络要求**: 确保新旧系统之间网络互通
5. **权限要求**: 确保有写入data目录的权限

## 七、典型工作流

### 场景A: 新部署环境快速恢复
```bash
# 1. 从生产环境导出
node scripts/export_daily_data.js https://prod.example.com prod_backup.json

# 2. 传输到新环境（如需要）
# scp prod_backup.json user@new-server:/path/to/

# 3. 导入到新环境
node scripts/import_daily_data.js http://localhost:9002 prod_backup.json

# 4. 验证
curl http://localhost:9002/api/coin-change-tracker/latest
```

### 场景B: 每日数据备份
```bash
# 导出到带日期的文件
node scripts/export_daily_data.js http://localhost:9002 backup_$(date +%Y%m%d).json

# 保留最近7天的备份
find . -name "backup_*.json" -mtime +7 -delete
```

### 场景C: 紧急数据恢复
```bash
# 1. 查找最新备份
ls -lt *.json | head -1

# 2. 快速恢复
node scripts/import_daily_data.js http://localhost:9002 backup_latest.json

# 3. 重启相关服务
pm2 restart all
```

## 八、性能参考

| 数据量 | 导出时间 | 导入时间 | 文件大小 |
|-------|---------|---------|---------|
| 小 (< 100KB) | < 1秒 | < 1秒 | < 0.1 MB |
| 中 (1-10MB) | 1-5秒 | 1-5秒 | 1-10 MB |
| 大 (> 10MB) | 5-30秒 | 5-30秒 | 10-100 MB |

## 九、错误代码

| 错误代码 | 含义 | 解决方法 |
|---------|------|---------|
| ECONNREFUSED | 连接被拒绝 | 检查URL和系统状态 |
| ETIMEDOUT | 连接超时 | 检查网络连接 |
| 400 | 请求格式错误 | 检查JSON格式 |
| 404 | 接口不存在 | 检查API路径 |
| 500 | 服务器错误 | 查看Flask日志 |

## 十、获取帮助

```bash
# 查看脚本帮助
node scripts/export_daily_data.js

# 查看完整文档
cat /home/user/webapp/DATA_SYNC_GUIDE.md

# 查看系统日志
pm2 logs flask-app --lines 50
```

---

**提示**: 在执行重要操作前，建议先在测试环境验证！
