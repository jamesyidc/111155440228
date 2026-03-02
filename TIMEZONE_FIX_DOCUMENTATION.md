# 跨日期时区问题修复文档

## 问题描述

### 现象
用户报告在跨日期时刻（UTC午夜前后），系统出现以下问题：
- 页面刷新出错
- 数据加载失败
- 前端无法正常显示

### 根本原因
1. **时区不一致**：监控脚本使用 `datetime.now()` 获取本地时区时间（UTC），而业务逻辑需要使用北京时间（UTC+8）
2. **文件名不匹配**：
   - UTC时间：2026-03-02 16:00（当天）
   - 北京时间：2026-03-03 00:00（次日）
   - 监控脚本创建文件：`coin_change_20260302.jsonl`
   - 前端API期望读取：`coin_change_20260303.jsonl`（北京时间日期）
3. **数据读取失败**：前端API无法找到正确日期的数据文件，导致加载失败

### 影响范围
- 27币涨跌幅条件单监控器
- 止损反手开单监控器
- 币种变化追踪器
- 所有基于日期命名的JSONL数据文件

## 解决方案

### 1. 创建统一的北京时间工具模块

**文件**：`utils/beijing_time.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北京时间工具函数
提供统一的北京时区时间处理
"""

from datetime import datetime, timezone, timedelta


def get_beijing_time():
    """获取北京时间（datetime对象）"""
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(timezone.utc).astimezone(beijing_tz)


def get_beijing_now_str(format_str='%Y-%m-%d %H:%M:%S'):
    """获取北京时间字符串"""
    return get_beijing_time().strftime(format_str)


def get_beijing_date_str(format_str='%Y%m%d'):
    """获取北京日期字符串"""
    return get_beijing_time().strftime(format_str)


def get_beijing_datetime_str():
    """获取北京日期时间字符串（适用于文件名）"""
    return get_beijing_time().strftime('%Y%m%d%H%M%S')
```

### 2. 修复监控脚本

#### 2.1 修复 `monitors/coin_change_conditional_order_monitor.py`

**修改前**：
```python
from datetime import datetime

log_file = log_dir / f'monitor_{datetime.now().strftime("%Y%m%d")}.log'

event = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    # ...
}
```

**修改后**：
```python
from utils.beijing_time import get_beijing_now_str, get_beijing_date_str, get_beijing_datetime_str

log_file = log_dir / f'monitor_{get_beijing_date_str()}.log'

event = {
    'timestamp': get_beijing_now_str(),
    # ...
}
```

#### 2.2 修复 `monitors/stoploss_reverse_monitor.py`

**批量替换**：
```bash
sed -i "s/datetime.now().strftime('%Y-%m-%d %H:%M:%S')/get_beijing_now_str()/g" monitors/stoploss_reverse_monitor.py
sed -i "s/datetime.now().strftime('%Y%m%d')/get_beijing_date_str()/g" monitors/stoploss_reverse_monitor.py
sed -i "s/datetime.now().strftime('%Y%m%d%H%M%S')/get_beijing_datetime_str()/g" monitors/stoploss_reverse_monitor.py
```

#### 2.3 修复 `source_code/coin_change_tracker.py`

**修改前**：
```python
print(f"[{datetime.now()}] Coin Change Tracker 启动...")
```

**修改后**：
```python
from utils.beijing_time import get_beijing_now_str

print(f"[{get_beijing_now_str()}] Coin Change Tracker 启动...")
```

### 3. 验证修复效果

#### 3.1 检查监控日志

```bash
pm2 logs coin-change-conditional-order-monitor --lines 10 --nostream
```

**预期输出**：
```
🔍 开始检查条件单触发 [北京时间 2026-03-03 00:09:41]
```

#### 3.2 检查API响应

```bash
curl -s "http://localhost:9002/api/okx-trading/coin-change-tpsl-overview/account_main" | python3 -m json.tool
```

**预期输出**：
```json
{
    "currentData": {
        "beijing_time": "2026-03-03 00:08:53",
        "data_available": true,
        "total_change": 9.47
    }
}
```

#### 3.3 检查数据文件

```bash
ls -la data/coin_change_tracker/coin_change_*.jsonl | tail -3
```

**预期输出**：
```
-rw-r--r-- 1 user user 2801812 Mar  1 15:59 data/coin_change_tracker/coin_change_20260301.jsonl
-rw-r--r-- 1 user user 2824390 Mar  2 15:58 data/coin_change_tracker/coin_change_20260302.jsonl
-rw-r--r-- 1 user user   19668 Mar  2 16:09 data/coin_change_tracker/coin_change_20260303.jsonl
```

## 技术细节

### 北京时间计算原理

1. **获取UTC时间**：`datetime.now(timezone.utc)`
2. **转换为北京时区**：`.astimezone(timezone(timedelta(hours=8)))`
3. **格式化输出**：`.strftime(format_str)`

### 跨日期场景示例

| UTC时间 | 北京时间 | 文件名（修复前） | 文件名（修复后） |
|---------|---------|-----------------|-----------------|
| 2026-03-02 15:59 | 2026-03-02 23:59 | coin_change_20260302.jsonl | coin_change_20260302.jsonl |
| 2026-03-02 16:00 | 2026-03-03 00:00 | coin_change_20260302.jsonl ❌ | coin_change_20260303.jsonl ✅ |
| 2026-03-02 16:01 | 2026-03-03 00:01 | coin_change_20260302.jsonl ❌ | coin_change_20260303.jsonl ✅ |

### 回退机制

API代码已经实现了回退机制（`app.py` 第17506-17517行）：
```python
# 尝试读取当天数据，如果不存在或为空，尝试前一天
file_to_read = None
if os.path.exists(coin_change_file) and os.path.getsize(coin_change_file) > 0:
    file_to_read = coin_change_file
else:
    # 尝试前一天的数据（跨日期时的回退机制）
    yesterday = beijing_now - timedelta(days=1)
    yesterday_date = yesterday.strftime('%Y%m%d')
    yesterday_file = os.path.join(coin_change_dir, f'coin_change_{yesterday_date}.jsonl')
    if os.path.exists(yesterday_file) and os.path.getsize(yesterday_file) > 0:
        file_to_read = yesterday_file
```

## 部署流程

### 1. 重启监控服务

```bash
pm2 restart coin-change-conditional-order-monitor stoploss-reverse-monitor
```

### 2. 验证服务状态

```bash
pm2 status
pm2 logs coin-change-conditional-order-monitor --lines 5 --nostream
pm2 logs stoploss-reverse-monitor --lines 5 --nostream
```

### 3. 验证API响应

```bash
curl -s "http://localhost:9002/api/okx-trading/coin-change-tpsl-overview/account_main"
```

## 修改文件清单

- ✅ `utils/beijing_time.py` - 新增北京时间工具模块
- ✅ `utils/__init__.py` - 新增包初始化文件
- ✅ `monitors/coin_change_conditional_order_monitor.py` - 修复时区问题
- ✅ `monitors/stoploss_reverse_monitor.py` - 修复时区问题
- ✅ `source_code/coin_change_tracker.py` - 修复时区问题

## 测试用例

### 测试场景1：北京时间跨日（UTC 16:00 = 北京 00:00）

1. 等待UTC时间到达16:00（北京时间00:00）
2. 检查监控日志是否显示北京时间标签
3. 检查数据文件是否使用新日期命名
4. 刷新前端页面，验证是否正常加载

### 测试场景2：API回退机制

1. 删除当天的数据文件
2. 调用API接口
3. 验证是否正确回退到前一天的数据

### 测试场景3：跨月跨年

1. 在月末/年末时刻测试
2. 验证日期计算是否正确

## 注意事项

1. **确保所有监控脚本都使用北京时间工具**
2. **新增监控脚本时必须使用 `utils/beijing_time.py`**
3. **日志文件名、数据文件名都应使用北京时间**
4. **时间戳显示给用户时应明确标注"北京时间"**

## 相关问题排查

### 问题1：页面刷新出错
**原因**：时区不一致导致文件名不匹配  
**解决**：使用统一的北京时间工具

### 问题2：数据加载失败
**原因**：API读取了错误日期的文件  
**解决**：确保监控脚本和API都使用北京时间

### 问题3：日志文件重复创建
**原因**：跨日期时创建了两个日期的日志文件  
**解决**：统一使用北京时间命名日志文件

## 未来优化建议

1. 考虑在所有Python脚本中统一导入北京时间工具
2. 在系统启动时打印当前使用的时区信息
3. 在日志中添加时区标签（UTC / Beijing）
4. 考虑使用环境变量配置时区

## Git提交信息

```
fix: 修复跨日期时区问题，统一使用北京时间

- 创建统一的北京时间工具模块 utils/beijing_time.py
- 修复监控脚本时区问题
- 所有日志文件名、数据文件名、时间戳均使用北京时区
- 验证：API正确返回北京时间数据
- 影响范围：27币条件单、止损反手、币种追踪器
```

## 参考资料

- Python datetime文档：https://docs.python.org/3/library/datetime.html
- 时区转换最佳实践：https://docs.python.org/3/library/datetime.html#datetime.datetime.astimezone
- OKX Trading系统文档：`STOPLOSS_REVERSE_SYSTEM.md`、`COIN_CHANGE_CONDITIONAL_ORDER_SYSTEM.md`
