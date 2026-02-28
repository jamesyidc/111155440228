# Panic V3 部署指南

## 🎯 设计理念

**从头开始重新设计，去除旧系统的冗余bug，保持简洁高效。**

## ✨ 核心特性

### 与旧系统对比

| 特性 | 旧系统 | V3系统 |
|------|--------|---------|
| 采集频率 | 5分钟 | **1分钟** |
| 数据存储 | 单文件 | **按日分文件** |
| 代码行数 | ~1000行 | **~400行** |
| Bug修复 | 多次补丁 | **重新设计** |
| 端口 | 5000 | **5001** |

### 数据需求实现

✅ **采集频率**: 每1分钟采集一次  
✅ **数据来源**: https://history.btc126.com/baocang/  
✅ **显示数据**:
- 恐慌清洗指数 (%)
- 1小时爆仓金额 (万美元)
- 24小时爆仓金额 (万美元)
- 24小时爆仓人数 (万人)
- 全网持仓量 (亿美元)
- 最后更新时间 (每1分钟更新)

✅ **图表1**: 24小时爆仓+全网持仓+恐慌指数
- 三线图
- 自动标记最高点
- 自动标记所有超过1.5亿(15000万$)的点

✅ **图表2**: 1小时爆仓金额
- 柱状图
- 只标记一个最高点

✅ **存储**: 按日期保存jsonl文件 (panic_YYYYMMDD.jsonl)

## 🚀 快速部署

### 前置条件

```bash
# 确认Python3和PM2已安装
python3 --version
pm2 --version

# 确认依赖包
pip3 install flask pytz requests
```

### 部署步骤

#### 1. 进入项目目录

```bash
cd /home/user/webapp/panic_v3
```

#### 2. 迁移旧数据（可选）

如果需要导入旧系统的数据：

```bash
python3 migrate.py
```

输出示例：
```
[开始] 从 /home/user/webapp/data/panic_jsonl/panic_wash_index.jsonl 迁移数据...
[统计] 总记录数: 27
[统计] 成功转换: 27
[统计] 失败记录: 0
[统计] 涵盖日期: 11 天
[保存] 20260201: 1 条记录 -> .../panic_20260201.jsonl
...
[完成] 数据迁移完成！
```

#### 3. 启动采集器

```bash
pm2 start collector.py --name panic-v3-collector --interpreter python3
```

验证：
```bash
pm2 logs panic-v3-collector --lines 20
```

预期输出：
```
[开始采集] 2026-02-11 14:29:55
[采集成功] 2026-02-11 14:29:59 | 1h爆仓: 3815.1万$ | 24h爆仓: 17584.61万$ | 爆仓人数: 7.33万人 | 全网持仓: 56.49亿$ | 恐慌指数: 0.1298 (中等恐慌)
[保存成功] 数据已保存到: .../panic_20260211.jsonl
[等待] 下次采集将在60秒后开始...
```

#### 4. 启动API服务

```bash
pm2 start app.py --name panic-v3-app --interpreter python3
```

验证：
```bash
# 测试API
curl -s http://localhost:5001/api/latest | python3 -m json.tool
```

预期输出：
```json
{
    "success": true,
    "data": {
        "liquidation_1h": 3815.1,
        "liquidation_24h": 17584.61,
        "liquidation_count_24h": 7.33,
        "open_interest": 56.49,
        "panic_index": 0.1298,
        "panic_level": "中等恐慌",
        "beijing_time": "2026-02-11 14:29:59"
    }
}
```

#### 5. 保存PM2配置

```bash
pm2 save
```

#### 6. 访问页面

浏览器打开: `http://your-domain:5001/`

## 📊 数据验证

### 检查数据文件

```bash
# 查看所有数据文件
ls -lh data/panic_*.jsonl

# 统计记录数
wc -l data/panic_*.jsonl

# 查看最新记录
tail -1 data/panic_$(date +%Y%m%d).jsonl | python3 -m json.tool
```

### 检查采集频率

```bash
# 实时监控采集器
pm2 logs panic-v3-collector
```

预期：每60秒采集一次

### 检查API响应

```bash
# 最新数据
curl -s http://localhost:5001/api/latest | python3 -m json.tool

# 24小时历史
curl -s "http://localhost:5001/api/history/24h" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"记录数: {data['count']}\")
print(f\"时间范围: {data['data'][0]['beijing_time']} ~ {data['data'][-1]['beijing_time']}\")
"
```

## 🔧 运维操作

### 重启服务

```bash
# 重启采集器
pm2 restart panic-v3-collector

# 重启API服务
pm2 restart panic-v3-app

# 重启所有V3服务
pm2 restart panic-v3-*
```

### 查看日志

```bash
# 实时日志
pm2 logs panic-v3-collector
pm2 logs panic-v3-app

# 历史日志
pm2 logs panic-v3-collector --lines 100
pm2 logs panic-v3-app --lines 100 --err

# 清空日志
pm2 flush panic-v3-collector
pm2 flush panic-v3-app
```

### 停止服务

```bash
# 停止采集器
pm2 stop panic-v3-collector

# 停止API服务
pm2 stop panic-v3-app

# 停止所有V3服务
pm2 stop panic-v3-*
```

### 删除服务

```bash
# 删除单个服务
pm2 delete panic-v3-collector
pm2 delete panic-v3-app

# 删除所有V3服务
pm2 delete panic-v3-*

# 保存配置
pm2 save
```

## 🐛 故障排查

### 问题1: 采集器不工作

**症状**: PM2显示在线，但没有新数据

**排查步骤**:

1. 查看错误日志
```bash
pm2 logs panic-v3-collector --err --lines 50
```

2. 手动测试采集
```bash
cd /home/user/webapp/panic_v3
python3 -c "from collector import get_btc126_data; print(get_btc126_data())"
```

3. 检查网络连接
```bash
curl -s "https://api.btc126.com/bicoin.php?from=24hbaocang&t=$(date +%s)000" | python3 -m json.tool
```

4. 重启采集器
```bash
pm2 restart panic-v3-collector
```

### 问题2: API返回空数据

**症状**: API返回 `{"success": true, "count": 0, "data": []}`

**排查步骤**:

1. 检查数据文件
```bash
ls -lh /home/user/webapp/panic_v3/data/
```

2. 检查今天的数据
```bash
cat /home/user/webapp/panic_v3/data/panic_$(date +%Y%m%d).jsonl
```

3. 确认采集器在运行
```bash
pm2 status panic-v3-collector
```

4. 查看Flask日志
```bash
pm2 logs panic-v3-app --lines 50
```

### 问题3: 前端不显示数据

**症状**: 页面加载但图表为空

**排查步骤**:

1. 打开浏览器开发者工具（F12）
2. 查看Console选项卡，是否有错误
3. 查看Network选项卡，检查API请求
4. 手动测试API
```bash
curl -s http://localhost:5001/api/latest
curl -s http://localhost:5001/api/history/24h
```

5. 清除浏览器缓存后刷新

### 问题4: 端口冲突

**症状**: Flask无法启动，提示端口占用

**解决方案**:

1. 检查端口占用
```bash
lsof -i :5001
```

2. 修改端口（如果需要）
```bash
# 编辑 app.py，修改最后一行
app.run(host='0.0.0.0', port=5002, debug=True)
```

3. 重新启动
```bash
pm2 restart panic-v3-app
```

## 📈 性能优化

### 数据清理

定期清理旧数据（保留最近30天）：

```bash
cd /home/user/webapp/panic_v3/data

# 找到30天前的日期
cutoff_date=$(date -d "30 days ago" +%Y%m%d)

# 删除旧文件
for file in panic_*.jsonl; do
    date_part=$(echo $file | grep -oP '\d{8}')
    if [ "$date_part" -lt "$cutoff_date" ]; then
        echo "删除旧数据: $file"
        rm "$file"
    fi
done
```

### 日志清理

定期清理PM2日志：

```bash
pm2 flush panic-v3-collector
pm2 flush panic-v3-app
```

## 🔄 数据备份

### 备份脚本

创建 `backup.sh`:

```bash
#!/bin/bash
# 备份Panic V3数据

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/user/webapp/backups/panic_v3"
SOURCE_DIR="/home/user/webapp/panic_v3/data"

mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/panic_v3_data_$DATE.tar.gz" -C "$SOURCE_DIR" .

echo "备份完成: $BACKUP_DIR/panic_v3_data_$DATE.tar.gz"

# 删除30天前的备份
find "$BACKUP_DIR" -name "panic_v3_data_*.tar.gz" -mtime +30 -delete
```

运行备份：
```bash
chmod +x backup.sh
./backup.sh
```

## 📝 监控脚本

创建 `monitor.sh`:

```bash
#!/bin/bash
# 监控Panic V3服务状态

echo "=== Panic V3 服务状态 ==="
pm2 status | grep panic-v3

echo ""
echo "=== 数据文件统计 ==="
wc -l /home/user/webapp/panic_v3/data/panic_*.jsonl

echo ""
echo "=== 最新数据 ==="
curl -s http://localhost:5001/api/latest | python3 -m json.tool

echo ""
echo "=== 24小时数据统计 ==="
curl -s "http://localhost:5001/api/history/24h" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"记录数: {data['count']}\")
    if data['data']:
        print(f\"最早: {data['data'][0]['beijing_time']}\")
        print(f\"最新: {data['data'][-1]['beijing_time']}\")
except:
    print('API错误')
"
```

运行监控：
```bash
chmod +x monitor.sh
./monitor.sh
```

## 🎯 下一步

1. **测试**: 观察24小时，确认数据采集正常
2. **验证**: 检查图表显示是否符合需求
3. **优化**: 根据实际使用调整采集频率或存储策略
4. **备份**: 设置定时备份任务
5. **监控**: 设置告警，监控服务状态

## ✅ 部署检查清单

- [ ] Python3和依赖包已安装
- [ ] 数据目录已创建 (`panic_v3/data/`)
- [ ] 旧数据已迁移（如果需要）
- [ ] 采集器已启动并正常运行
- [ ] API服务已启动并响应正常
- [ ] PM2配置已保存
- [ ] 前端页面可访问
- [ ] 数据每分钟更新
- [ ] 图表显示正常
- [ ] 备份脚本已配置

## 📞 技术支持

遇到问题请参考：

1. **本文档** - 完整的部署和故障排查指南
2. **README.md** - 系统概述和API文档
3. **代码注释** - collector.py 和 app.py
4. **PM2日志** - 实时运行日志
5. **Git历史** - 提交记录和变更说明

---

**版本**: V3.0  
**创建时间**: 2026-02-11  
**维护者**: System Admin  
**状态**: 生产环境
