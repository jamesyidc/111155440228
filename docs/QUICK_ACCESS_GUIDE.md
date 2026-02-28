# 快速访问指南

## 🌐 访问地址

### Web管理界面
```
https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/data-sync-manager
```

**功能：**
- 📊 查看系统状态
- ⚙️ 配置发送端/接收端
- 📡 查看所有30个数据接口
- 🔍 搜索和过滤接口
- 📖 查看使用示例

---

## 📡 核心接口

### 1. 获取所有接口列表
```bash
GET /api/data-sync/sender/catalog
```

### 2. 获取单个端点数据（需认证）
```bash
GET /api/data-sync/sender/data/{CODE}

Headers:
  X-Request-From: https://your-system.com
  X-System-ID: your_system_id
  Authorization: Bearer your-token (可选)
```

**示例：**
```bash
# 获取最新价格追踪数据
curl -H "X-Request-From: https://your-system.com" \
     https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/api/data-sync/sender/data/PT001
```

### 3. 批量获取数据（需认证）
```bash
POST /api/data-sync/sender/batch

Headers:
  X-Request-From: https://your-system.com
  X-System-ID: your_system_id
  Authorization: Bearer your-token (可选)

Body:
{
  "codes": ["PT001", "PB001", "AN001"],
  "params": {"limit": 100}
}
```

---

## 📚 快速文档索引

| 文档 | 说明 | 重要性 |
|------|------|--------|
| [DATA_FORMAT_SPECIFICATION.md](./DATA_FORMAT_SPECIFICATION.md) | 数据格式规范 | ⭐⭐⭐ |
| [MAIN_URL_AUTH_COMPLETION_REPORT.md](./MAIN_URL_AUTH_COMPLETION_REPORT.md) | 主网址认证说明 | ⭐⭐ |
| [FRONTEND_API_DISPLAY_COMPLETION.md](./FRONTEND_API_DISPLAY_COMPLETION.md) | 前端接口展示 | ⭐⭐ |
| [FINAL_COMPLETE_SUMMARY.md](./FINAL_COMPLETE_SUMMARY.md) | 完整项目总结 | ⭐⭐ |

---

## 🔑 30个数据端点速查

### 价格 (PT/PS/PB)
- **PT001** - 最新价格追踪
- **PT002** - 价格历史
- **PS001** - 价格速度
- **PB001** - 价格基准

### SAR (SAR)
- **SAR001** - 当前周期
- **SAR002** - 偏离统计
- **SAR003** - 斜率数据

### 锚定 (AN)
- **AN001** - 利润最新
- **AN002** - 利润历史
- **AN003** - 系统状态
- **AN004** - 系统持仓

### OKX (OKX)
- **OKX001** - 市场行情
- **OKX002** - 持仓列表
- **OKX003** - 挂单列表
- **OKX004** - 交易日志
- **OKX005** - 账户限额

### 信号 (ES/EX/ME)
- **ES001** - 逃顶信号
- **ES002** - 逃顶统计
- **EX001** - 极值追踪
- **ME001** - 重大事件

### 指标 (CC/PI/FG)
- **CC001** - 币种变化
- **CC002** - 变化基准
- **PI001** - 恐慌指数
- **FG001** - 恐惧贪婪

### 其他 (LQ/CI/SR/V1V2/SYS)
- **LQ001** - 清算数据
- **CI001** - 加密指数
- **SR001** - 支撑阻力
- **V1V2001** - V1V2数据
- **SYS001** - 数据健康
- **SYS002** - 采集器状态

---

## ⚙️ 配置示例

### 发送端配置
```json
{
  "system_info": {
    "main_url": "https://your-system.com"
  },
  "sender": {
    "enabled": true,
    "receiver_main_urls": [
      "https://receiver1.com",
      "https://receiver2.com"
    ],
    "auth_config": {
      "auth_enabled": false,
      "auth_token": ""
    }
  }
}
```

### 接收端配置
```json
{
  "system_info": {
    "main_url": "https://your-system.com"
  },
  "receiver": {
    "enabled": true,
    "sender_main_url": "https://sender.com",
    "sync_config": {
      "auto_sync": true,
      "sync_interval_seconds": 300
    }
  }
}
```

---

## 🧪 测试命令

### 测试系统
```bash
cd /home/user/webapp
python3 test_data_sync_system.py
```

### 测试前端
```bash
cd /home/user/webapp
python3 test_frontend_display.py
```

---

## 📊 系统状态检查

### 发送端状态
```bash
curl http://localhost:5000/api/data-sync/sender/status
```

### 接收端状态
```bash
curl http://localhost:5000/api/data-sync/receiver/status
```

### 数据目录
```bash
curl http://localhost:5000/api/data-sync/sender/catalog
```

---

## 🎯 常见任务

### 1. 查看所有接口
👉 访问: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/data-sync-manager

### 2. 搜索特定接口
👉 在首页搜索框输入关键词（如：OKX、价格、锚定）

### 3. 复制使用示例
👉 每个接口都提供了curl命令示例

### 4. 配置发送端
👉 切换到"发送端"标签，填写配置后保存

### 5. 配置接收端
👉 切换到"接收端"标签，填写发送端URL后保存

### 6. 启动自动同步
👉 在"接收端"标签点击"启动自动同步"按钮

---

**最后更新：** 2026-02-04  
**系统版本：** v1.1.0
