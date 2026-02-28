# 加密货币监控系统 - 完整备份

> 📅 备份时间: 2026-02-07 00:24:56  
> 📦 备份版本: 2.0  
> 🔧 系统版本: Production

## 📋 备份内容清单

### 1. 代码文件 (code/)
- **app.py** - Flask主应用 (344个路由)
- **source_code/** - 88个Python源代码文件
  - 17个数据采集器 (collectors)
  - 5个管理器 (managers)
  - 多个工具和辅助模块
- **major-events-system/** - 重大事件监控系统
- **templates/** - 87个HTML模板文件
- **static/** - 静态资源文件

### 2. 配置文件 (config/)
- **ecosystem.config.js** - PM2进程管理配置 (23个进程)
- **requirements.txt** - Python依赖清单 (230个包)
- **pm2_dump.json** - PM2进程状态快照
- **apt_packages.txt** - 系统软件包列表 (642个包)
- **configs/** - 14个应用配置文件
  - telegram_config.json - TG机器人配置
  - okx_api_config.json - OKX API配置
  - trading_config.json - 交易配置
  - 等等...

### 3. 数据文件 (data/)
- **databases/** - SQLite数据库文件
  - anchor_profit_real.db
  - price_comparison.db
- **jsonl_samples/** - 近7天的JSONL数据 (~741MB)
- **coin_change_tracker/** - 27币追涨基准数据 (14个文件)

### 4. 文档文件 (docs/)
- **DEPLOYMENT_GUIDE.md** - 完整部署指南
- **ROUTES_MAPPING.md** - 344个Flask路由映射文档
- **markdown/** - 566个Markdown文档
  - 系统文档
  - 修复报告
  - 使用指南
  - 开发日志

### 5. 部署脚本
- **restore.sh** - 自动恢复脚本 (一键部署)
- **checksums.md5** - 文件完整性校验 (1477个文件)

## 🚀 快速开始

### 方法一: 自动恢复 (推荐)

```bash
# 1. 解压备份文件
tar -xzf webapp_complete_backup_20260207_002456.tar.gz

# 2. 进入备份目录
cd webapp_complete_backup_20260207_002456

# 3. 运行恢复脚本 (需要root权限)
sudo ./restore.sh
```

恢复脚本会自动完成:
- ✅ 检查系统要求
- ✅ 安装所有依赖 (Python, Node.js, PM2等)
- ✅ 创建用户和目录结构
- ✅ 恢复所有代码和配置
- ✅ 恢复数据文件
- ✅ 启动23个PM2进程
- ✅ 验证安装

### 方法二: 手动恢复

详细步骤请参考 `deployment/DEPLOYMENT_GUIDE.md`

## 📊 系统架构

### PM2 进程列表 (23个)

| # | 进程名 | 类型 | 功能 | 采集频率 |
|---|--------|------|------|----------|
| 1 | flask-app | Web | Flask主应用 | - |
| 2 | panic-collector | 采集器 | 恐慌指数采集 | 30秒 |
| 3 | signal-collector | 采集器 | 信号采集 | 60秒 |
| 4 | liquidation-1h-collector | 采集器 | 1小时爆仓数据 | 2秒 |
| 5 | fear-greed-collector | 采集器 | 恐惧贪婪指数 | 120秒 |
| 6 | depth-score-collector | 采集器 | 深度评分 | 60秒 |
| 7 | crypto-index-collector | 采集器 | 加密指数 | 60秒 |
| 8 | position-collector | 采集器 | 持仓数据 | 60秒 |
| 9 | v1v2-collector | 采集器 | V1V2成交量 | 60秒 |
| 10 | price-speed-collector | 采集器 | 价格速度 | 60秒 |
| 11 | gdrive-detector | 采集器 | 趋势检测 | 60秒 |
| 12 | star-system-collector | 采集器 | 星级系统 | 60秒 |
| 13 | funding-rate-collector | 采集器 | 资金费率 | 60秒 |
| 14 | extreme-tracking-collector | 采集器 | 极值追踪 | 10秒 |
| 15 | sar-slope-collector | 采集器 | SAR斜率 | 60秒 |
| 16 | sar-slope-bias-collector | 采集器 | SAR偏差 | 60秒 |
| 17 | kline-collector | 采集器 | K线数据 | 60秒 |
| 18 | price-comparison-collector | 采集器 | 价格对比 | 60秒 |
| 19 | data-health-monitor | 监控 | 数据健康监控 | - |
| 20 | major-events-monitor | 监控 | 重大事件监控 | - |
| 21 | telegram-manager | 管理器 | TG消息管理 | - |
| 22 | breakthrough-manager | 管理器 | 突破管理 | - |
| 23 | unified-monitor-manager | 管理器 | 统一监控 | - |

### Web路由系统

- **总路由数**: 344个
- **页面路由**: 88个
- **API路由**: 245个
- **其他路由**: 11个

主要功能模块:
- 📊 首页概览
- 🚨 恐慌监控
- 💰 27币追涨
- 📈 价格对比
- ⭐ 星级系统
- 🎯 仓位系统
- 📡 数据健康监控
- 🤖 TG机器人管理
- 🔥 重大事件监控 (9个事件)

## 🔧 系统要求

### 硬件要求
- CPU: 2核及以上
- RAM: 4GB及以上 (推荐8GB)
- 磁盘: 20GB可用空间

### 软件要求
- OS: Ubuntu 20.04+ / Debian 11+
- Python: 3.8+
- Node.js: 14+
- PM2: 最新版
- SQLite3

## 📝 重要配置

恢复后需要配置的文件:

1. **configs/telegram_config.json**
   - Telegram Bot Token
   - Chat IDs

2. **configs/okx_api_config.json**
   - OKX API Key
   - API Secret
   - Passphrase

3. **configs/trading_config.json**
   - 交易参数
   - 风控设置

## 🛠️ 常用命令

```bash
# PM2管理
su - user -c "pm2 status"              # 查看所有进程状态
su - user -c "pm2 logs"                # 查看所有日志
su - user -c "pm2 logs flask-app"      # 查看特定进程日志
su - user -c "pm2 restart all"         # 重启所有进程
su - user -c "pm2 stop all"            # 停止所有进程

# 数据验证
md5sum -c checksums.md5                # 验证文件完整性

# 服务测试
curl http://localhost:5000             # 测试Flask应用
curl http://localhost:5000/api/stats   # 测试API
```

## 🔐 安全建议

1. 修改默认端口 (5000)
2. 配置Nginx反向代理
3. 启用SSL/TLS
4. 配置防火墙规则
5. 定期备份数据
6. 保护API密钥
7. 限制访问IP

## 📞 故障排查

### Flask应用无法启动
```bash
su - user -c "pm2 logs flask-app"      # 查看错误日志
su - user -c "cd /home/user/webapp && python3 app.py"  # 直接运行测试
```

### 采集器报错
```bash
su - user -c "pm2 logs <collector-name>"  # 查看特定采集器日志
```

### 数据库错误
```bash
sqlite3 /home/user/webapp/data/anchor_profit_real.db ".schema"  # 检查数据库结构
```

## 📈 监控和维护

1. **日志管理**: PM2自动管理日志轮转
2. **进程监控**: PM2自动重启崩溃进程
3. **数据备份**: 建议每天备份data目录
4. **系统更新**: 定期更新Python依赖和系统包

## 📄 文档索引

- `deployment/DEPLOYMENT_GUIDE.md` - 完整部署指南
- `docs/ROUTES_MAPPING.md` - 路由映射文档
- `config/ecosystem.config.js` - PM2配置
- `config/requirements.txt` - Python依赖
- `restore.sh` - 自动恢复脚本

## ✅ 验证清单

恢复完成后请检查:

- [ ] 所有23个PM2进程运行正常
- [ ] Flask应用可访问 (http://localhost:5000)
- [ ] 数据库文件存在且可读
- [ ] 配置文件已正确设置
- [ ] 日志正常输出
- [ ] API接口响应正常

## 🎯 下一步

1. 配置Telegram Bot Token
2. 配置OKX API Keys
3. 设置防火墙规则
4. 配置Nginx (可选)
5. 设置定时备份
6. 监控系统运行状态

---

**版本**: 2.0  
**创建时间**: 2026-02-07 00:24:56  
**备份文件**: webapp_complete_backup_20260207_002456.tar.gz  
**预计大小**: ~2GB (压缩后)

有问题请参考详细文档或查看日志文件。
