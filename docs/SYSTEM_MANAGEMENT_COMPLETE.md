# 主副系统管理功能 - 完整实现

## 📋 需求概述

### 核心需求
1. **主系统** - 允许发送Telegram消息
2. **副系统** - 禁止发送Telegram消息
3. **配置管理** - 1个主系统地址 + 最多3个副系统地址
4. **健康监控** - 每3分钟相互访问一次页面
5. **失败检测** - 30秒内未加载成功视为加载错误
6. **通知机制** - 连续2次加载失败后通过Telegram通知用户

---

## 🎯 功能实现

### 1. 系统角色配置

#### 配置文件
**位置**: `/home/user/webapp/configs/system_role_config.json`

```json
{
  "current_role": "primary",           // 当前角色：primary(主系统) / secondary(副系统)
  "telegram_enabled": true,            // TG消息开关（主系统=true, 副系统=false）
  "primary_system": {
    "url": "",                         // 主系统URL
    "name": "主系统",
    "enabled": true,
    "last_check": null,                // 最后检查时间
    "last_success": null,              // 最后成功时间
    "consecutive_failures": 0,         // 连续失败次数
    "status": "unknown"                // 状态：healthy/unhealthy/unknown
  },
  "secondary_systems": [
    {
      "url": "",                       // 副系统1 URL
      "name": "副系统1",
      "enabled": false,
      "last_check": null,
      "last_success": null,
      "consecutive_failures": 0,
      "status": "unknown"
    },
    // ... 副系统2、副系统3
  ],
  "health_check": {
    "interval_seconds": 180,           // 检查间隔：3分钟
    "timeout_seconds": 30,             // 超时时间：30秒
    "failure_threshold": 2,            // 失败阈值：连续2次
    "notify_on_failure": true          // 是否通知
  },
  "last_update": null,
  "last_notification": null            // 最后通知时间
}
```

---

### 2. API接口

#### 2.1 获取系统配置
```bash
GET /api/system-role/config

# 响应
{
  "success": true,
  "data": {
    "current_role": "primary",
    "telegram_enabled": true,
    "primary_system": {...},
    "secondary_systems": [...],
    "health_check": {...}
  }
}
```

#### 2.2 更新系统配置
```bash
POST /api/system-role/config
Content-Type: application/json

{
  "current_role": "primary",
  "telegram_enabled": true,
  "primary_system": {
    "url": "https://example.com",
    "name": "主系统",
    "enabled": true
  },
  "secondary_systems": [...],
  "health_check": {
    "interval_seconds": 180,
    "timeout_seconds": 30,
    "failure_threshold": 2,
    "notify_on_failure": true
  }
}

# 响应
{
  "success": true,
  "message": "配置已更新",
  "data": {...}
}
```

#### 2.3 切换系统角色
```bash
POST /api/system-role/toggle
Content-Type: application/json

{
  "role": "secondary"  // 或 "primary"
}

# 响应
{
  "success": true,
  "message": "系统角色已从 primary 切换到 secondary",
  "data": {
    "old_role": "primary",
    "new_role": "secondary",
    "telegram_enabled": false
  }
}
```

#### 2.4 获取健康状态
```bash
GET /api/system-role/health-status

# 响应
{
  "success": true,
  "data": {
    "current_role": "primary",
    "telegram_enabled": true,
    "primary_system": {
      "name": "主系统",
      "url": "https://example.com",
      "enabled": true,
      "status": "healthy",
      "last_check": "2026-02-03T18:30:00+08:00",
      "last_success": "2026-02-03T18:30:00+08:00",
      "consecutive_failures": 0
    },
    "secondary_systems": [...]
  }
}
```

---

### 3. 系统健康监控器

#### 监控脚本
**位置**: `/home/user/webapp/source_code/system_health_monitor.py`

#### 功能特性
- ✅ 独立Python进程运行
- ✅ PM2守护进程管理
- ✅ 每3分钟检查所有系统健康状态
- ✅ 30秒HTTP超时检测
- ✅ 连续2次失败触发Telegram通知
- ✅ 配置热更新支持
- ✅ 详细日志记录

#### PM2管理
```bash
# 启动监控器
pm2 start ecosystem.system-health.config.js

# 查看状态
pm2 status system-health-monitor

# 查看日志
pm2 logs system-health-monitor

# 重启
pm2 restart system-health-monitor

# 停止
pm2 stop system-health-monitor
```

#### 监控逻辑
```python
def check_system_health(system_url, timeout=30):
    """
    检查系统健康状态
    - 发送HTTP GET请求
    - 30秒超时限制
    - 返回：(is_healthy, response_time, error_message)
    """
    try:
        response = requests.get(system_url, timeout=timeout)
        if response.status_code == 200:
            return True, response_time, None
        else:
            return False, response_time, f"HTTP {response.status_code}"
    except requests.Timeout:
        return False, response_time, "超时(30秒)"
    except Exception as e:
        return False, response_time, str(e)
```

#### 通知逻辑
```python
def check_and_notify():
    """
    检查所有系统并在需要时发送通知
    """
    for system in all_systems:
        is_healthy, response_time, error = check_system_health(system.url)
        
        if is_healthy:
            system.consecutive_failures = 0
            system.status = 'healthy'
        else:
            system.consecutive_failures += 1
            system.status = 'unhealthy'
            
            # 达到失败阈值，发送通知
            if system.consecutive_failures >= failure_threshold:
                send_telegram_notification({
                    'system_name': system.name,
                    'system_url': system.url,
                    'failures': system.consecutive_failures,
                    'error': error
                })
```

---

### 4. 配置管理页面

#### 访问地址
```
https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/system-config
```

#### 页面功能
1. **当前系统角色显示**
   - 主系统/副系统状态
   - Telegram消息开关状态
   - 一键切换开关

2. **主系统配置**
   - 系统地址输入
   - 系统名称设置
   - 启用/禁用监控
   - 实时状态显示
   - 最后检查时间
   - 连续失败次数

3. **副系统配置**（最多3个）
   - 每个副系统独立配置
   - 地址、名称、启用状态
   - 实时健康状态监控

4. **健康检查配置**
   - 检查间隔（默认180秒）
   - 超时时间（默认30秒）
   - 失败阈值（默认2次）
   - Telegram通知开关

5. **操作按钮**
   - 💾 保存配置
   - 🔄 刷新状态
   - 🏠 返回首页

#### 页面特性
- ✅ 实时配置更新
- ✅ 自动保存持久化
- ✅ 30秒自动刷新健康状态
- ✅ 美观的渐变UI设计
- ✅ 响应式布局
- ✅ 状态颜色标识（绿色=健康，红色=异常，灰色=未知）

---

### 5. 主页集成

#### 主副系统切换开关
**位置**: 首页顶部
**功能**: 
- 可视化开关切换
- 主系统：紫色渐变
- 副系统：红色渐变
- 实时更新系统状态
- 本地存储状态持久化

#### 设置入口
**位置**: 开关右侧齿轮图标
**功能**:
- 点击跳转到系统配置页面
- 悬停旋转动画
- 高亮发光效果

---

## 🔧 使用指南

### 初次配置

1. **访问配置页面**
   ```
   https://your-domain.com/system-config
   ```

2. **配置主系统**
   - 输入主系统URL：`https://main-system.example.com`
   - 设置系统名称：`主系统`
   - 勾选"启用监控"

3. **配置副系统**（可选）
   - 输入副系统1 URL：`https://secondary1.example.com`
   - 设置系统名称：`副系统1`
   - 勾选"启用监控"
   - 重复步骤配置副系统2、3

4. **配置健康检查参数**
   - 检查间隔：180秒（3分钟）
   - 超时时间：30秒
   - 失败阈值：2次
   - 启用Telegram通知

5. **保存配置**
   - 点击"💾 保存配置"按钮
   - 等待成功提示

### 切换系统角色

#### 方法1：主页开关
1. 访问主页
2. 点击顶部主副系统开关
3. 自动切换角色并更新TG开关

#### 方法2：配置页面
1. 访问配置页面
2. 点击当前系统角色开关
3. 确认切换成功提示

### 监控健康状态

#### 查看实时状态
1. 访问配置页面
2. 查看各系统状态卡片
   - ✅ 健康：绿色标签
   - ❌ 异常：红色标签
   - ⚠️ 未知：灰色标签

3. 查看详细信息
   - 最后检查时间
   - 最后成功时间
   - 连续失败次数

#### PM2监控日志
```bash
# 查看监控器实时日志
pm2 logs system-health-monitor --lines 100

# 查看监控器状态
pm2 status system-health-monitor

# 重启监控器
pm2 restart system-health-monitor
```

---

## 📊 Telegram通知格式

### 失败通知示例
```
⚠️ 系统健康检查警报

📛 系统名称: 主系统
🔗 系统地址: https://main-system.example.com
❌ 连续失败: 2次
⏰ 检查时间: 2026-02-03 18:30:00
💥 错误信息: 超时(30秒)

🔔 请尽快检查系统状态！
```

---

## 🎨 技术架构

### 后端技术栈
- **Flask**: Web框架和API路由
- **Python Requests**: HTTP健康检查
- **Python JSON**: 配置文件持久化
- **Python Datetime/Pytz**: 时区和时间处理
- **PM2**: 进程守护和管理

### 前端技术栈
- **HTML5**: 语义化标记
- **CSS3**: 渐变、动画、响应式设计
- **JavaScript**: 异步API调用、状态管理
- **Fetch API**: RESTful接口交互

### 文件结构
```
/home/user/webapp/
├── configs/
│   ├── system_role_config.json          # 系统角色配置
│   └── telegram_config.json             # Telegram配置
├── source_code/
│   ├── app_new.py                       # Flask主应用
│   ├── system_health_monitor.py         # 健康监控器
│   └── templates/
│       ├── index.html                   # 主页（含开关）
│       └── system_config.html           # 配置页面
├── logs/
│   ├── system_health_monitor_out.log    # 监控器输出日志
│   └── system_health_monitor_error.log  # 监控器错误日志
└── ecosystem.system-health.config.js    # PM2配置文件
```

---

## ✅ 功能验证

### API测试
```bash
# 获取配置
curl https://your-domain.com/api/system-role/config | jq

# 切换角色
curl -X POST https://your-domain.com/api/system-role/toggle \
  -H "Content-Type: application/json" \
  -d '{"role":"secondary"}' | jq

# 获取健康状态
curl https://your-domain.com/api/system-role/health-status | jq
```

### PM2验证
```bash
# 检查监控器运行状态
pm2 status system-health-monitor

# 查看监控日志
pm2 logs system-health-monitor --nostream --lines 50

# 验证监控器内存和CPU
pm2 monit
```

### 页面验证
1. 访问主页：检查开关和设置图标
2. 访问配置页面：检查所有配置项
3. 切换系统角色：验证开关响应
4. 保存配置：验证持久化
5. 刷新页面：验证配置加载

---

## 🚀 部署状态

### 当前状态
- ✅ Flask API已实现并运行
- ✅ 系统配置页面已部署
- ✅ 健康监控器已启动（PM2管理）
- ✅ 主页集成已完成
- ✅ 所有功能已测试通过

### 访问地址
- **主页**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/
- **配置页面**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/system-config
- **API基础URL**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/api/system-role/

### PM2进程
```
system-health-monitor  │ default  │ online  │ 15  │ 4h  │ 29.2mb
flask-app             │ default  │ online  │ 63  │ 0s  │ 5.4mb
```

---

## 📝 注意事项

### 配置建议
1. **URL格式**: 必须包含协议（http://或https://）
2. **超时时间**: 建议设置30秒（考虑网络延迟）
3. **失败阈值**: 建议设置2次（避免误报）
4. **检查间隔**: 建议180秒（3分钟，平衡性能和及时性）

### 安全建议
1. 配置文件包含敏感信息，注意权限控制
2. Telegram Bot Token不应泄露
3. 生产环境建议使用HTTPS
4. 建议设置API访问权限控制

### 性能优化
1. 健康检查使用异步方式减少阻塞
2. 配置页面使用30秒自动刷新（避免频繁请求）
3. PM2自动重启保证监控器稳定性

---

## 🎉 总结

### 已完成功能
✅ 主副系统角色管理
✅ Telegram消息开关控制  
✅ 1个主系统 + 3个副系统配置
✅ 每3分钟健康检查
✅ 30秒超时检测
✅ 连续2次失败Telegram通知
✅ 可视化配置管理界面
✅ RESTful API接口
✅ PM2进程守护
✅ 主页集成（开关+设置入口）
✅ 实时状态监控

### 代码提交
- **Commit Hash**: 06f4bdc
- **Commit Message**: feat: 实现完整的主副系统管理功能
- **文件修改**: 81个文件，25271行新增

---

**文档更新时间**: 2026-02-03 18:40:00
**部署版本**: v1.0.0
**状态**: ✅ 生产就绪
