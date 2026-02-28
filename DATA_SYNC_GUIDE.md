# 数据同步系统使用文档

## 系统概述

数据同步系统提供了在不同部署环境之间快速同步JSONL数据的能力。当你备份恢复系统后，可以使用这个功能快速获取最新的当天数据。

## 功能特点

1. **自动数据导出** - 一键导出当天所有关键JSONL数据
2. **批量数据导入** - 批量导入数据到新系统
3. **自动备份** - 导入前自动备份原文件
4. **数据完整性** - 显示文件大小和行数，便于验证
5. **交易日逻辑** - 自动识别交易日（北京时间02:00切日）

## 系统架构

```
┌─────────────┐                    ┌─────────────┐
│  旧系统 A   │                    │  新系统 B   │
│             │                    │             │
│  Flask API  │ ──────导出────►   │  Flask API  │
│  /export    │    (JSON文件)     │  /import    │
└─────────────┘                    └─────────────┘
      ▲                                   ▲
      │                                   │
      │                                   │
 export_daily_data.js            import_daily_data.js
 (导出脚本)                       (导入脚本)
```

## API接口说明

### 1. 数据导出接口

**URL**: `/api/data-sync/export`  
**方法**: `GET`  
**描述**: 导出当天所有关键JSONL数据

**响应格式**:
```json
{
  "success": true,
  "date": "20260224",
  "datetime_readable": "2026-02-24 20:01:33",
  "total_files": 17,
  "total_size": 165824,
  "total_size_mb": 0.16,
  "files": [
    {
      "path": "data/coin_alert_settings/settings.jsonl",
      "filename": "settings.jsonl",
      "size": 17522,
      "line_count": 73,
      "content": "{...}\n{...}\n..."
    }
  ]
}
```

**导出的数据文件**:
- `data/coin_change_tracker/coin_change_YYYYMMDD.jsonl` - 币种涨跌数据
- `data/coin_change_tracker/rsi_YYYYMMDD.jsonl` - RSI数据
- `data/coin_change_tracker/price_speed_YYYYMMDD.jsonl` - 价格速度数据
- `data/anchor_daily/anchor_data_YYYY-MM-DD.jsonl` - 锚定数据
- `data/dashboard_jsonl/dashboard_data_YYYYMMDD.jsonl` - 仪表板数据
- `data/escape_signal_daily/escape_signal_YYYYMMDD.jsonl` - 逃顶信号数据
- `data/coin_alert_settings/settings.jsonl` - 币种预警设置
- `data/okx_tpsl_settings/*.jsonl` - OKX止盈止损设置
- `data/favorite_symbols.jsonl` - 收藏币种
- `data/account_position_limits.jsonl` - 账户持仓限制

### 2. 数据导入接口

**URL**: `/api/data-sync/import`  
**方法**: `POST`  
**描述**: 批量导入JSONL数据

**请求格式**:
```json
{
  "files": [
    {
      "path": "data/coin_alert_settings/settings.jsonl",
      "content": "{...}\n{...}\n..."
    }
  ]
}
```

**响应格式**:
```json
{
  "success": true,
  "imported_count": 17,
  "failed_count": 0,
  "total_size": 165824,
  "total_size_mb": 0.16,
  "imported_files": [
    {
      "path": "data/coin_alert_settings/settings.jsonl",
      "size": 17522,
      "line_count": 73
    }
  ],
  "failed_files": []
}
```

**安全特性**:
- 导入前自动备份原文件
- 备份文件格式: `{原文件名}.backup_{时间戳}`
- 例如: `settings.jsonl.backup_20260224_120137`

## 使用方法

### 场景1: 从旧系统导出数据

```bash
# 导出旧系统的数据
node scripts/export_daily_data.js https://9002-old-system.sandbox.novita.ai

# 或指定输出文件名
node scripts/export_daily_data.js https://9002-old-system.sandbox.novita.ai backup_20260224.json
```

**输出示例**:
```
🚀 开始导出数据...
📍 源系统: https://9002-old-system.sandbox.novita.ai
💾 输出文件: data_export_20260224.json
🔗 API地址: https://9002-old-system.sandbox.novita.ai/api/data-sync/export
📥 响应状态码: 200
....
✅ 数据接收完成

📊 导出统计:
  日期: 20260224
  时间: 2026-02-24 20:01:33
  文件数量: 17
  总大小: 0.16 MB

📁 导出的文件列表:
  1. data/coin_alert_settings/settings.jsonl (17.11 KB, 73 行)
  2. data/okx_tpsl_settings/account_main_history.jsonl (54.37 KB, 98 行)
  ...

✅ 数据已成功导出到: data_export_20260224.json
💡 下一步: 使用 import_daily_data.js 脚本导入到新系统
```

### 场景2: 导入数据到新系统

```bash
# 将导出的数据导入到新系统
node scripts/import_daily_data.js https://9002-new-system.sandbox.novita.ai data_export_20260224.json
```

**输出示例**:
```
🚀 开始导入数据...
📍 目标系统: https://9002-new-system.sandbox.novita.ai
📁 数据文件: data_export_20260224.json
✅ 数据文件已加载
  导出日期: 20260224
  文件数量: 17
  总大小: 0.16 MB

🔗 API地址: https://9002-new-system.sandbox.novita.ai/api/data-sync/import
📤 准备发送数据...

⏳ 正在发送数据，请稍候...
📥 响应状态码: 200
✅ 响应接收完成

📊 导入统计:
  成功: 17 个文件
  失败: 0 个文件
  总大小: 0.16 MB

✅ 成功导入的文件:
  1. data/coin_alert_settings/settings.jsonl (17.11 KB, 73 行)
  2. data/okx_tpsl_settings/account_main_history.jsonl (54.37 KB, 98 行)
  ...

✅ 数据导入完成！
🎉 所有文件都已成功导入！
```

### 场景3: 完整的数据迁移流程

```bash
# 步骤1: 从旧系统导出数据
node scripts/export_daily_data.js https://9002-old.sandbox.novita.ai backup.json

# 步骤2: 将数据传输到新服务器（如果需要）
# scp backup.json user@new-server:/home/user/webapp/

# 步骤3: 在新系统上导入数据
node scripts/import_daily_data.js https://9002-new.sandbox.novita.ai backup.json

# 步骤4: 验证数据完整性
curl http://localhost:9002/api/coin-change-tracker/latest
```

## 常见问题 (FAQ)

### Q1: 如何确认数据导出成功？

**A**: 查看输出日志中的以下信息:
- 响应状态码应为 200
- 文件数量 > 0
- 总大小 > 0
- 每个文件都显示了正确的行数

### Q2: 导入会覆盖原数据吗？

**A**: 是的，但是：
1. 导入前会自动备份原文件
2. 备份文件命名格式: `{原文件}.backup_{时间戳}`
3. 可以通过备份文件恢复原数据

### Q3: 如何恢复备份的数据？

**A**: 
```bash
# 查找备份文件
ls -la data/*/*.backup_*

# 恢复特定文件（去掉.backup_时间戳后缀）
cp data/coin_alert_settings/settings.jsonl.backup_20260224_120137 \
   data/coin_alert_settings/settings.jsonl
```

### Q4: 支持哪些数据文件？

**A**: 当前支持以下类型的JSONL文件:
- 币种变化追踪数据 (coin_change_tracker)
- RSI指标数据
- 价格速度数据
- 锚定数据 (anchor_daily)
- 仪表板数据
- 逃顶信号数据
- 币种预警设置
- OKX止盈止损设置
- 收藏币种列表
- 账户持仓限制

### Q5: 交易日逻辑是什么？

**A**: 
- 交易日在北京时间 02:00 切换
- 00:00-01:59 期间，认为是前一天的数据
- 02:00-23:59 期间，认为是当天的数据
- 这符合加密货币交易的习惯

### Q6: 如何验证导入后的数据？

**A**: 可以通过以下方式验证:
```bash
# 检查文件大小和行数
wc -l data/coin_alert_settings/settings.jsonl

# 查看文件最后几行
tail -5 data/coin_alert_settings/settings.jsonl

# 通过API查询
curl http://localhost:9002/api/coin-change-tracker/latest
```

### Q7: 脚本执行失败怎么办？

**A**: 检查以下几点:
1. 确保Node.js已安装 (`node --version`)
2. 检查URL是否正确（包含http://或https://）
3. 确保目标系统正在运行
4. 检查网络连接
5. 查看错误日志中的详细信息

### Q8: 可以定期自动同步吗？

**A**: 可以，使用cron定时任务:
```bash
# 编辑crontab
crontab -e

# 每天凌晨3点自动同步（交易日已切换）
0 3 * * * cd /home/user/webapp && node scripts/export_daily_data.js http://localhost:9002 daily_backup_$(date +\%Y\%m\%d).json

# 或使用PM2定时任务
pm2 start scripts/export_daily_data.js --name daily-sync --cron "0 3 * * *"
```

## 技术细节

### 文件大小限制
- 单个文件: 无限制（理论上）
- 总大小: 建议 < 100MB（取决于网络和内存）
- 超大文件建议分批导入

### 性能优化
- 数据压缩: API响应已启用gzip压缩
- 批量处理: 一次导入多个文件
- 并发控制: 建议逐个系统同步，避免并发冲突

### 安全建议
1. **内网使用** - 建议在内网环境使用
2. **HTTPS** - 生产环境使用HTTPS协议
3. **认证** - 可添加API Token认证（待实现）
4. **数据加密** - 敏感数据可先加密再传输（待实现）

## 故障排查

### 问题: 导出时提示连接超时

**原因**: 目标系统未响应或网络问题

**解决**:
```bash
# 检查系统是否运行
curl http://localhost:9002/health

# 检查PM2状态
pm2 status flask-app

# 重启Flask应用
pm2 restart flask-app
```

### 问题: 导入失败部分文件

**原因**: 目标目录不存在或权限问题

**解决**:
```bash
# 检查目录权限
ls -la data/

# 创建缺失的目录
mkdir -p data/coin_change_tracker
mkdir -p data/okx_tpsl_settings

# 修复权限
chmod 755 data/
chmod 644 data/*/*.jsonl
```

### 问题: JSON解析错误

**原因**: 数据文件格式错误或损坏

**解决**:
```bash
# 验证JSON格式
python3 -m json.tool < test_export.json > /dev/null

# 检查文件编码
file test_export.json

# 重新导出数据
node scripts/export_daily_data.js http://localhost:9002 test_export_new.json
```

## 更新日志

### v1.0.0 (2026-02-24)
- ✅ 实现数据导出API `/api/data-sync/export`
- ✅ 实现数据导入API `/api/data-sync/import`
- ✅ 创建导出脚本 `export_daily_data.js`
- ✅ 创建导入脚本 `import_daily_data.js`
- ✅ 支持自动备份原文件
- ✅ 支持交易日逻辑（02:00切日）
- ✅ 完整的测试验证

### 未来计划
- 🔄 添加API Token认证
- 🔄 支持增量同步（只同步变化的文件）
- 🔄 支持数据加密传输
- 🔄 Web UI界面管理
- 🔄 同步状态监控和告警

## 联系支持

如有问题或建议，请联系系统管理员。

---

**最后更新**: 2026-02-24  
**版本**: v1.0.0  
**维护者**: System Administrator
