# 页面定时截图系统配置说明

## 📸 功能概述

系统会自动对指定页面进行定时截图，外部程序可以通过API访问这些截图。

### 核心特性
1. ⏱️ **每1分钟截图一次**
2. 📁 **保存为JPG格式**
3. 🌐 **提供HTTP API访问**
4. ⏰ **30分钟延迟展示**（显示30分钟前的截图）
5. 🗑️ **自动清理**（只保留最近3小时的数据）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /home/user/webapp
pip3 install playwright
playwright install chromium
```

### 2. 运行截图监控

```bash
# 方式1：直接运行（前台）
python3 scripts/screenshot_monitor.py

# 方式2：后台运行
nohup python3 scripts/screenshot_monitor.py > logs/screenshot-monitor.log 2>&1 &

# 方式3：使用PM2（推荐）
pm2 start scripts/screenshot_monitor.py --name screenshot-monitor --interpreter python3
pm2 save
```

### 3. 访问截图

**查看器页面**：http://localhost:9002/screenshots/viewer

**API接口**：
- 最新截图：`GET /api/screenshots/latest`
- 截图列表：`GET /api/screenshots/list`
- 图片文件：`GET /api/screenshots/image/{filename}`

## 📖 API文档

### 1. 获取最新截图（30分钟延迟）

```bash
GET /api/screenshots/latest
```

**响应示例**：
```json
{
  "success": true,
  "screenshot": {
    "filename": "screenshot_20260224_223045.jpg",
    "timestamp": "2026-02-24 22:30:45",
    "url": "/api/screenshots/image/screenshot_20260224_223045.jpg",
    "size": 245678
  }
}
```

### 2. 获取截图列表

```bash
GET /api/screenshots/list?limit=50
```

**参数**：
- `limit`: 返回数量限制（默认100）

**响应示例**：
```json
{
  "success": true,
  "total": 50,
  "screenshots": [
    {
      "filename": "screenshot_20260224_223045.jpg",
      "timestamp": "2026-02-24 22:30:45",
      "url": "/api/screenshots/image/screenshot_20260224_223045.jpg",
      "size": 245678
    },
    ...
  ]
}
```

### 3. 获取截图图片

```bash
GET /api/screenshots/image/screenshot_20260224_223045.jpg
```

**响应**：JPEG图片文件

## 🔧 配置

编辑 `scripts/screenshot_monitor.py`：

```python
# 目标URL
TARGET_URL = "http://localhost:9002/coin-change-tracker"

# 截图间隔（秒）
SCREENSHOT_INTERVAL = 60

# 保留时长（小时）
KEEP_HOURS = 3

# 延迟展示（分钟）
DISPLAY_DELAY_MINUTES = 30
```

## 📂 文件结构

```
/home/user/webapp/
├── scripts/
│   └── screenshot_monitor.py        # 截图监控脚本
├── data/
│   └── screenshots/                 # 截图存储目录
│       ├── screenshot_20260224_223045.jpg
│       ├── screenshot_20260224_223145.jpg
│       └── metadata.json            # 元数据文件
└── logs/
    └��─ screenshot-monitor.log       # 运行日志
```

## 💻 外部程序调用示例

### Python示例

```python
import requests

# 获取最新截图信息
response = requests.get('http://localhost:9002/api/screenshots/latest')
data = response.json()

if data['success']:
    screenshot = data['screenshot']
    print(f"截图时间: {screenshot['timestamp']}")
    print(f"图片URL: {screenshot['url']}")
    
    # 下载图片
    img_response = requests.get(f"http://localhost:9002{screenshot['url']}")
    with open('latest_screenshot.jpg', 'wb') as f:
        f.write(img_response.content)
    print("截图已保存")
```

### JavaScript示例

```javascript
// 获取最新截图
async function getLatestScreenshot() {
    const response = await fetch('http://localhost:9002/api/screenshots/latest');
    const data = await response.json();
    
    if (data.success) {
        const screenshot = data.screenshot;
        console.log('截图时间:', screenshot.timestamp);
        
        // 显示图片
        const img = document.createElement('img');
        img.src = `http://localhost:9002${screenshot.url}`;
        document.body.appendChild(img);
    }
}
```

### curl示例

```bash
# 获取最新截图信息
curl http://localhost:9002/api/screenshots/latest

# 下载截图图片
curl -o latest.jpg "http://localhost:9002/api/screenshots/image/screenshot_20260224_223045.jpg"
```

## 🎯 使用场景

### 1. 监控系统状态
外部程序每30秒获取一次截图，监控页面是否正常显示

### 2. 历史回溯
查看30分钟前的页面状态，用于对比和分析

### 3. 自动化报告
定期生成报告，附带页面截图

### 4. 远程监控
在其他服务器上访问API，实时监控页面状态

## 🔍 监控和管理

### 查看运行状态

```bash
# PM2方式
pm2 status screenshot-monitor
pm2 logs screenshot-monitor --lines 50

# 进程方式
ps aux | grep screenshot_monitor.py
```

### 查看截图数量

```bash
ls -lh data/screenshots/ | wc -l
du -sh data/screenshots/
```

### 清理所有截图

```bash
rm -f data/screenshots/screenshot_*.jpg
```

### 重启服务

```bash
# PM2方式
pm2 restart screenshot-monitor

# 手动方式
pkill -f screenshot_monitor.py
python3 scripts/screenshot_monitor.py &
```

## ⚙️ PM2配置示例

添加到 `ecosystem.config.js`：

```javascript
{
  name: 'screenshot-monitor',
  script: 'scripts/screenshot_monitor.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  autorestart: true,
  watch: false,
  max_memory_restart: '500M',
  error_file: '/home/user/webapp/logs/screenshot-error.log',
  out_file: '/home/user/webapp/logs/screenshot-out.log',
  log_date_format: 'YYYY-MM-DD HH:mm:ss'
}
```

然后：

```bash
pm2 reload ecosystem.config.js
pm2 save
```

## 🚨 注意事项

1. **存储空间**：每张截图约200-500KB，3小时约360-900MB
2. **性能影响**：每次截图会刷新页面，注意对服务器的影响
3. **延迟展示**：API返回的是30分钟前的截图，不是实时的
4. **自动清理**：超过3小时的截图会自动删除
5. **浏览器资源**：Chromium会占用一定内存，建议定期重启

## 🐛 故障排查

### 截图失败

1. 检查Playwright是否正确安装
2. 检查目标URL是否可访问
3. 查看错误日志：`logs/screenshot-error.log`

### API返回空

1. 确认截图服务正在运行
2. 检查 `data/screenshots/` 目录是否有文件
3. 等待至少30分钟（冷启动需要时间）

### 图片无法加载

1. 检查文件是否存在
2. 检查Flask服务是否运行
3. 查看浏览器控制台错误信息

## 📊 性能优化

### 减少截图频率

```python
SCREENSHOT_INTERVAL = 120  # 改为2分钟一次
```

### 降低图片质量

```python
page.screenshot(path=output_path, quality=70)  # 降低为70%
```

### 调整保留时长

```python
KEEP_HOURS = 2  # 只保留2小时
```

## 🔗 相关文件

- 截图脚本：`scripts/screenshot_monitor.py`
- Flask API：`app.py`（新增截图相关路由）
- 存储目录：`data/screenshots/`
- 配置文档：`SCREENSHOT_SYSTEM.md`（本文件）

## 📝 更新日志

- **2026-02-24**: 初始版本
  - 实现每1分钟自动截图
  - 提供HTTP API访问接口
  - 30分钟延迟展示
  - 自动清理3小时前的数据
  - 创建Web查看器页面
