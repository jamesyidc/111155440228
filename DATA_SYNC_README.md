# 数据同步系统 - 快速开始

> 一键同步JSONL数据的完整解决方案

## 🚀 10秒快速开始

### 导出数据
```bash
node scripts/export_daily_data.js https://源系统URL
```

### 导入数据
```bash
node scripts/import_daily_data.js https://目标系统URL 导出的数据文件.json
```

## 📖 文档导航

| 文档 | 说明 | 适用人群 |
|-----|------|---------|
| [完整指南](DATA_SYNC_GUIDE.md) | 详细的使用说明、FAQ、故障排查 | 所有用户 |
| [快速参考](DATA_SYNC_QUICK_REF.md) | 常用命令速查表 | 熟练用户 |
| [开发报告](DATA_SYNC_DEVELOPMENT_REPORT.md) | 技术实现细节、测试结果 | 开发者 |
| [最终总结](DATA_SYNC_FINAL_SUMMARY.md) | 项目总览、交付成果 | 项目经理 |

## 🎬 演示视频
```bash
# 运行交互式演示脚本
bash scripts/demo_data_sync.sh
```

## 💡 典型使用场景

### 场景1: 备份恢复后同步数据
```bash
# 从旧系统导出
node scripts/export_daily_data.js https://9002-old.sandbox.novita.ai backup.json

# 导入到新系统
node scripts/import_daily_data.js https://9002-new.sandbox.novita.ai backup.json
```

### 场景2: 每日定时备份
```bash
# 导出当天数据（可配置cron定时任务）
node scripts/export_daily_data.js http://localhost:9002 daily_$(date +%Y%m%d).json
```

## ✅ 功能特性

- ✅ **自动识别交易日** - 北京时间02:00自动切日
- ✅ **批量处理** - 一次导出/导入多个文件
- ✅ **自动备份** - 导入前自动备份原文件
- ✅ **数据验证** - 显示文件大小和行数
- ✅ **详细日志** - 彩色输出和进度显示

## 📊 测试结果

```
✅ 导出: 17个文件，0.16 MB - 成功
✅ 导入: 17个文件全部导入 - 成功
✅ 备份: 自动创建备份文件 - 正常
```

## 🔧 API接口

### 导出接口
```http
GET /api/data-sync/export
```

### 导入接口
```http
POST /api/data-sync/import
Content-Type: application/json

{
  "files": [
    {"path": "data/settings.jsonl", "content": "..."}
  ]
}
```

## 📞 需要帮助？

1. 查看 [完整指南](DATA_SYNC_GUIDE.md)
2. 查看 [FAQ](DATA_SYNC_GUIDE.md#常见问题-faq)
3. 运行演示脚本：`bash scripts/demo_data_sync.sh`

## 📝 版本信息

- **版本**: v1.0.0
- **发布日期**: 2026-02-24
- **状态**: ✅ 生产就绪

---

**开发者**: System Administrator  
**最后更新**: 2026-02-24
