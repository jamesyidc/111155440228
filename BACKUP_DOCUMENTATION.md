# Complete Project Backup - Documentation

**Date**: 2026-03-03  
**Backup Location**: `/tmp/webapp_full_backup_20260303_043527.tar.gz`  
**Backup Size**: 259 MB (compressed from 3.1 GB)

---

## 📦 Backup Overview

This is a **COMPLETE PROJECT BACKUP** including all source code, full historical data (not limited to 7 days), configurations, and documentation.

### What's Included

✅ **Source Code** (160 Python files)
- Main Flask application
- All Python API files
- Monitoring scripts
- Utility functions

✅ **Data** (660 JSONL files - 3.1 GB)
- **FULL HISTORICAL DATA** (not limited to 7 days)
- Midnight hedge system records (configs, execution, P&L)
- Panic signal data (complete history)
- Position tracking data (complete history)

✅ **Frontend** (140 HTML templates)
- All HTML templates
- Static assets (CSS, JavaScript, images)

✅ **Configuration**
- PM2 ecosystem config
- Application configurations
- Python requirements

✅ **Documentation** (1,035 Markdown files)
- System documentation
- README files
- Technical guides

### What's Excluded

❌ `logs/` - Log files (~219 MB, regenerated)  
❌ `node_modules/` - Dependencies (~34 MB, reinstallable)  
❌ `backups/` - Previous backups (avoid recursion)  
❌ `__pycache__/` - Compiled Python files (auto-generated)

---

## 🚀 Quick Deployment

```bash
# Extract backup
tar -xzf webapp_full_backup_20260303_043527.tar.gz

# Navigate to directory
cd webapp_full_backup_20260303_043527

# Install dependencies
pip3 install -r requirements.txt
npm install -g pm2

# Create logs directory
mkdir -p logs

# Configure environment
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_HOST=0.0.0.0
FLASK_PORT=9002
# Add your API keys here
EOF

# Start services
pm2 start ecosystem.config.js
pm2 save

# Verify deployment
pm2 status
curl http://localhost:9002/health
```

---

## 📄 Additional Documentation

Three comprehensive documentation files are included in `/tmp/`:

1. **DEPLOYMENT_GUIDE.md** (3.9 KB)
   - Step-by-step deployment instructions
   - System architecture overview
   - Configuration details
   - Troubleshooting guide
   - Security considerations

2. **BACKUP_SUMMARY.md** (7.5 KB)
   - Detailed backup statistics
   - Complete directory structure
   - Included/excluded items
   - Key features
   - Restoration commands
   - Verification checklist

3. **BACKUP_VERIFICATION.md**
   - Verification results
   - Quick access commands
   - Documentation references

---

## 🔧 System Components

### Core Services

1. **Flask Application** (port 9002)
   - Main API server
   - Trading endpoints
   - Midnight hedge system APIs

2. **Midnight Hedge Monitor**
   - Executes at Beijing 00:00:00 daily
   - Independent long/short controls
   - Real-time P&L tracking
   - Manual reset required after execution

3. **Background Monitors**
   - Stop loss reverse monitor
   - Bottom signal monitors
   - Coin change predictor
   - Other specialized monitors

---

## 📊 Data Structure

```
data/
├── midnight_hedge_orders/
│   ├── configs/              # Account configurations
│   ├── execution_records/    # Daily execution logs
│   ├── pnl_records/         # Profit/loss tracking
│   └── logs/                # Monitor logs
├── panic_signals/           # Panic detection data (full history)
├── positions/               # Position tracking (full history)
└── [other data directories] # Additional historical data
```

**Total Data Size**: 3.1 GB (660 JSONL files)  
**Data Retention**: FULL HISTORY (not limited to 7 days)

---

## 🔐 Security Notes

1. **API Keys**: Not included in backup - must be configured manually
2. **Environment File**: Create `.env` with your credentials after extraction
3. **Permissions**: Set `chmod 600 .env` for security
4. **Firewall**: Configure rules for port 9002
5. **SSL/TLS**: Use reverse proxy (nginx) for HTTPS in production

---

## ✅ Deployment Checklist

After extracting the backup:

- [ ] Extract archive to deployment location
- [ ] Install Python dependencies (`pip3 install -r requirements.txt`)
- [ ] Install Node.js and PM2 (`npm install -g pm2`)
- [ ] Create logs directory (`mkdir -p logs`)
- [ ] Configure `.env` file with API keys
- [ ] Review `ecosystem.config.js` for custom settings
- [ ] Start PM2 services (`pm2 start ecosystem.config.js`)
- [ ] Verify Flask app is running (port 9002)
- [ ] Check all monitors are active (`pm2 status`)
- [ ] Test API endpoints (`curl http://localhost:9002/health`)
- [ ] Verify data files are accessible
- [ ] Access web interface
- [ ] Configure firewall rules
- [ ] Setup SSL/TLS (if needed)
- [ ] Setup PM2 startup script (`pm2 startup`)
- [ ] Save PM2 configuration (`pm2 save`)

---

## 🎯 Key Features

### 1. Complete Data History
- ALL 660 JSONL files included
- NOT limited to 7 days
- Full historical data from inception
- Complete midnight hedge system records
- All panic signal history

### 2. Independent Execution Control
- Long and short orders controlled separately
- Each account has independent settings
- Manual reset required after execution
- Prevents duplicate order submission

### 3. Beijing Timezone Support
- All timestamps in Beijing time (UTC+8)
- Midnight hedge executes at 00:00 Beijing time
- Consistent timezone across all components

### 4. Comprehensive Monitoring
- Real-time P&L tracking
- Execution record logging
- Multiple background monitors
- PM2 process management

---

## 📝 Git Commit History

Key commits included in this backup:

- `0b42529` - feat: 独立执行权限控制防止重复下单
- `84483c1` - style: 增大0点0分对冲底仓盈亏显示字体
- `0b67870` - test: add test data for midnight hedge
- `07ce6b5` - fix: 修复对冲底仓监控器API调用方法
- `3a627e0` - feat: 0点0分对冲底仓系统显示实际盈亏

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
pm2 logs --lines 100
pm2 restart all
```

### Port Already in Use
```bash
sudo lsof -i :9002
sudo kill -9 <PID>
```

### Permission Issues
```bash
chmod -R 755 data/
chmod -R 755 logs/
chmod +x monitors/*.py
```

### Data Files Missing
```bash
ls -lh data/
find data/ -name "*.jsonl" | wc -l  # Should show 660
```

---

## 📈 Monitoring & Maintenance

### Daily Checks
```bash
pm2 status
pm2 logs --lines 20 --nostream
df -h
```

### Weekly Maintenance
```bash
find logs/ -name "*.log" -mtime +30 -delete
du -sh data/ logs/
```

### Monthly Tasks
- Review and archive old JSONL files
- Update dependencies
- Check system resource usage
- Create new backup

---

## 📞 Support

For detailed deployment instructions and troubleshooting, refer to:
- `/tmp/DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `/tmp/BACKUP_SUMMARY.md` - Backup details and statistics
- `/tmp/BACKUP_VERIFICATION.md` - Verification results

---

## ✨ Summary

**Backup Archive**: `webapp_full_backup_20260303_043527.tar.gz`  
**Location**: `/tmp/`  
**Size**: 259 MB compressed (3.1 GB uncompressed)  
**Compression Ratio**: ~8.4%

**Contents**:
- 160 Python source files
- 660 JSONL data files (3.1 GB - FULL HISTORY)
- 140 HTML templates
- 1,035 Markdown documentation files
- Complete configuration files
- PM2 ecosystem config

**Ready for immediate deployment** - Extract, install dependencies, configure, and start services.

---

**Backup Date**: 2026-03-03  
**Documentation Version**: 1.0
