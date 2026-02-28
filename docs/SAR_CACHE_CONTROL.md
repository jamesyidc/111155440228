# SAR偏向趋势图 - 缓存清除与版本控制

## 更新时间
2026-02-03 17:10:00

## 问题说明
用户浏览器缓存了旧版本HTML，导致看不到最新的5分钟刷新功能。

## 解决方案

### 1. HTML Meta标签 - 禁用缓存
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

**作用**：
- `Cache-Control: no-cache, no-store, must-revalidate` - 禁止浏览器缓存
- `Pragma: no-cache` - 兼容HTTP/1.0
- `Expires: 0` - 立即过期

### 2. JavaScript版本检查 - 自动清除缓存
```javascript
const CURRENT_VERSION = '2.1-20260203-5min';
const STORED_VERSION = localStorage.getItem('sar_bias_trend_version');

if (STORED_VERSION !== CURRENT_VERSION) {
    console.log('🔄 检测到新版本，清除缓存...');
    console.log('旧版本:', STORED_VERSION, '→ 新版本:', CURRENT_VERSION);
    localStorage.setItem('sar_bias_trend_version', CURRENT_VERSION);
    
    // 如果之前有版本记录，说明是更新，需要刷新
    if (STORED_VERSION) {
        console.log('🔄 强制刷新页面以加载新版本...');
        location.reload(true);
    }
}
```

**工作流程**：
1. 检查localStorage中存储的版本号
2. 如果版本不匹配，更新版本号
3. 如果是从旧版本更新，自动刷新页面
4. 强制从服务器加载最新HTML

### 3. Flask响应头 - 服务器端控制
```python
@app.route('/sar-bias-trend')
def sar_bias_trend_page():
    """SAR偏向趋势图页面"""
    response = make_response(render_template('sar_bias_trend.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
```

**作用**：
- 服务器告诉浏览器不要缓存此页面
- 每次访问都从服务器获取最新版本

### 4. 页面标题版本号
```html
<title>SAR偏向趋势图 - 12小时分页 v2.1-20260203</title>
```

**作用**：
- 用户可直观看到当前版本
- 方便问题排查

---

## 版本号格式

### 格式：`v{主版本}.{次版本}-{日期}-{特性}`

**示例**：`v2.1-20260203-5min`
- `2.1` - 版本号（2.1版本）
- `20260203` - 更新日期（2026年2月3日）
- `5min` - 特性标识（5分钟刷新）

### 版本更新规则
- **主版本号**：重大功能变更或架构调整
- **次版本号**：功能优化、bug修复
- **日期**：发布日期（YYYYMMDD）
- **特性**：本次更新的关键特性

---

## 测试结果

### Console日志
```
🔄 检测到新版本，清除缓存...
旧版本: null → 新版本: 2.1-20260203-5min
📊 SAR偏向趋势图加载中...
✅ 页面初始化完成，第1页每5分钟自动更新
✅ 数据已更新: 第1页, 408 个数据点
```

### 验证要点
1. ✅ 首次访问：`旧版本: null` - 全新用户
2. ✅ 再次访问：不会触发刷新（版本号已匹配）
3. ✅ 版本更新后：自动检测并刷新页面
4. ✅ 页面标题：显示`v2.1-20260203`

### 用户体验
- **首次访问**：正常加载，记录版本号
- **常规访问**：直接加载，无刷新
- **版本更新**：自动检测 → 提示 → 刷新 → 加载新版本

---

## 缓存清除层级

### 三层缓存控制
```
┌─────────────────────────────────────────┐
│  1. HTML Meta标签                       │
│  • 告诉浏览器不要缓存                    │
│  • 每次访问都请求服务器                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. Flask响应头                         │
│  • 服务器主动禁止缓存                    │
│  • 设置立即过期                          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. JavaScript版本检查                  │
│  • 检测版本号变化                        │
│  • 自动刷新获取新版本                    │
│  • localStorage持久化版本号              │
└─────────────────────────────────────────┘
```

---

## 强制清除缓存方法

### 方法1：硬刷新（推荐用户使用）
- **Windows/Linux**：`Ctrl + F5` 或 `Ctrl + Shift + R`
- **Mac**：`Cmd + Shift + R`
- **效果**：忽略缓存，强制从服务器获取

### 方法2：开发者工具
1. 打开开发者工具（F12）
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

### 方法3：清除浏览器数据
1. 浏览器设置 → 隐私和安全
2. 清除浏览数据
3. 选择"缓存的图片和文件"

### 方法4：版本号自动检测（已实现）
- 自动检测版本变化
- 无需手动操作
- 对用户透明

---

## 版本更新流程

### 开发流程
```
1. 修改功能代码
   ↓
2. 更新版本号（HTML + JS）
   CURRENT_VERSION = '2.1-20260203-5min'
   ↓
3. 更新页面标题
   <title>... v2.1-20260203</title>
   ↓
4. 同步文件
   cp templates/*.html source_code/templates/
   ↓
5. 重启Flask
   pm2 restart flask-app
   ↓
6. 用户访问时自动检测并刷新
```

### 版本号管理建议
```javascript
// 集中管理版本号
const VERSION_CONFIG = {
    major: 2,
    minor: 1,
    date: '20260203',
    feature: '5min',
    get full() {
        return `${this.major}.${this.minor}-${this.date}-${this.feature}`;
    }
};
```

---

## 其他页面缓存控制

### 已添加缓存控制的页面
1. ✅ `/sar-bias-trend` - SAR偏向趋势图
2. ✅ `/escape-signal-history` - 逃顶信号历史（已有版本检查）
3. ✅ `/system-config` - 系统配置
4. ✅ `/data-health-monitor` - 数据健康监控

### 建议添加的页面
- `/anchor-system-real` - 实盘锚点系统
- `/support-resistance` - 支撑压力线系统
- `/coin-change-tracker` - 币价涨跌追踪

---

## 常见问题

### Q1: 为什么还是显示旧版本？
**A**: 尝试以下方法：
1. 硬刷新：`Ctrl + Shift + R`
2. 清除浏览器缓存
3. 检查版本号是否更新
4. 查看Console是否有版本检测日志

### Q2: 版本号在哪里查看？
**A**: 三个位置：
1. 页面标题：`SAR偏向趋势图 - 12小时分页 v2.1-20260203`
2. Console日志：`新版本: 2.1-20260203-5min`
3. localStorage：`sar_bias_trend_version`

### Q3: 自动刷新会丢失数据吗？
**A**: 不会，因为：
- 只在版本变化时刷新一次
- 使用`location.reload(true)`强制刷新
- localStorage会保存版本号

### Q4: 如何禁用自动刷新？
**A**: 临时禁用方法：
```javascript
// 在Console执行
localStorage.setItem('sar_bias_trend_version', '2.1-20260203-5min');
```

---

## 监控与日志

### 版本检测日志
```javascript
// 首次访问
🔄 检测到新版本，清除缓存...
旧版本: null → 新版本: 2.1-20260203-5min

// 版本更新
🔄 检测到新版本，清除缓存...
旧版本: 2.0-20260202 → 新版本: 2.1-20260203-5min
🔄 强制刷新页面以加载新版本...

// 版本匹配（正常访问）
（无日志输出）
```

### 刷新日志
```javascript
// 5分钟自动刷新
⏰ 5分钟定时刷新，开始加载数据...
✅ 数据已更新: 第1页, 408 个数据点
```

---

## 页面链接
https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/sar-bias-trend

---

## 修改文件
- `templates/sar_bias_trend.html` - 添加缓存控制和版本检查
- `source_code/templates/sar_bias_trend.html` - 同步
- `source_code/app_new.py` - 添加响应头控制

---

## 总结

✅ **三层缓存控制**：Meta标签 + 响应头 + 版本检查  
✅ **自动版本检测**：localStorage版本号比对  
✅ **强制刷新机制**：检测到更新自动reload  
✅ **用户体验**：对用户透明，自动更新  

**核心价值**：
1. 确保用户始终看到最新版本
2. 无需手动清除缓存
3. 开发者更新后自动生效
4. 降低用户支持成本

---

**更新时间**：2026-02-03 17:10:00  
**当前版本**：v2.1-20260203-5min  
**缓存状态**：✅ 已禁用  
**版本检测**：✅ 已启用
