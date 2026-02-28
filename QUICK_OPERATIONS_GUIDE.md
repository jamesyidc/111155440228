# 🚀 快速操作指南

## 📋 常用命令

### 系统健康检查
```bash
cd /home/user/webapp
./scripts/check_system_health.sh
```

### PM2进程管理

#### 查看所有进程状态
```bash
pm2 status
```

#### 查看实时监控
```bash
pm2 monit
```

#### 查看进程详情
```bash
pm2 show flask-app
```

### 日志管理

#### 查看所有日志
```bash
pm2 logs
```

#### 查看特定服务日志
```bash
pm2 logs flask-app
pm2 logs okx-tpsl-monitor
pm2 logs coin-change-predictor
```

#### 查看最新50行日志
```bash
pm2 logs flask-app --lines 50
```

#### 清空日志
```bash
pm2 flush
```

### 服务控制

#### 重启所有服务
```bash
pm2 restart all
```

#### 重启特定服务
```bash
pm2 restart flask-app
pm2 restart okx-tpsl-monitor
```

#### 停止服务
```bash
pm2 stop flask-app
```

#### 启动服务
```bash
pm2 start flask-app
```

#### 删除进程
```bash
pm2 delete flask-app
```

#### 重新加载所有服务
```bash
cd /home/user/webapp
pm2 delete all
pm2 start ecosystem.config.js
```

### 保存配置
```bash
pm2 save
```

## 🌐 访问地址

### Web界面
- **公网访问**: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai
- **本地访问**: http://localhost:9002

## 📊 数据管理

### 查看JSONL文件
```bash
# 币种预警设置
cat data/coin_alert_settings/settings.jsonl | tail -1 | python3 -m json.tool

# OKX TPSL配置
cat data/okx_tpsl_settings/account_main_tpsl.jsonl | tail -1 | python3 -m json.tool

# 查看最新数据
ls -lt data/okx_tpsl_settings/ | head
```

### 备份数据
```bash
cd /home/user/webapp
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ config/
```

### 统计数据
```bash
# JSONL文件数量
find data -name "*.jsonl" | wc -l

# 数据目录大小
du -sh data/

# 最新更新的文件
find data -name "*.jsonl" -type f -mtime -1
```

## 🔧 配置文件

### 环境变量
```bash
nano .env
```

### OKX账户配置
```bash
nano okx_accounts.json
```

### PM2配置
```bash
nano ecosystem.config.js
```

## 📈 监控系统状态

### 系统资源
```bash
# 内存使用
pm2 ls | grep -E 'mem|MB'

# CPU使用
top -b -n 1 | grep python3
```

### 数据库连接测试
```bash
# 测试币种变化追踪API
curl http://localhost:9002/api/coin-change-tracker/latest | python3 -m json.tool
```

## 🚨 故障排查

### Flask应用无响应
```bash
# 查看Flask日志
pm2 logs flask-app --lines 100

# 重启Flask
pm2 restart flask-app

# 检查端口占用
netstat -tlnp | grep 9002
```

### 数据采集异常
```bash
# 查看数据收集器日志
pm2 logs signal-collector
pm2 logs okx-tpsl-monitor

# 检查数据文件权限
ls -la data/okx_tpsl_settings/

# 手动触发采集
python3 source_code/signal_collector.py
```

### PM2进程频繁重启
```bash
# 查看错误日志
pm2 logs <process-name> --err

# 检查内存限制
pm2 show <process-name>

# 增加内存限制
# 编辑 ecosystem.config.js 中的 max_memory_restart
```

## 📞 紧急命令

### 完全重启系统
```bash
cd /home/user/webapp
pm2 delete all
pm2 start ecosystem.config.js
pm2 save
```

### 恢复默认配置
```bash
# 备份当前配置
cp ecosystem.config.js ecosystem.config.js.backup

# 恢复原配置
git checkout ecosystem.config.js

# 重新启动
pm2 delete all
pm2 start ecosystem.config.js
```

## 📝 日常维护

### 每日检查清单
1. ✅ 运行健康检查脚本
2. ✅ 查看PM2进程状态
3. ✅ 检查错误日志
4. ✅ 验证数据更新
5. ✅ 测试关键API

### 每周维护
1. 🔄 清理旧日志 (`pm2 flush`)
2. 🔄 备份数据目录
3. 🔄 检查磁盘空间
4. 🔄 更新依赖包

## 🎯 性能优化

### 内存优化
```bash
# 查看内存使用最高的进程
pm2 list | sort -k10 -n

# 重启高内存进程
pm2 restart <high-memory-process>
```

### 日志优化
```bash
# 限制日志文件大小
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

## 📚 更多资源

- PM2文档: https://pm2.keymetrics.io/docs/usage/quick-start/
- Flask文档: https://flask.palletsprojects.com/
- 部署报告: `cat DEPLOYMENT_COMPLETE_20260224.md`

---

*最后更新: 2026-02-24*
