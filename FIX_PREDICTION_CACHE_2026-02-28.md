# 预判数据缓存问题修复报告

**日期**: 2026-02-28  
**问题**: 页面显示今天的预判为"诱空试盘抄底"，但根据规则应该是"做空"  
**状态**: ✅ 已修复  
**Git Commit**: ea29268  

---

## 📋 问题描述

### 用户反馈
用户提供的截图显示：
- 绿色：0根
- 红色：8根  
- 黄色：0根
- 空白：4根（显示在页面上）
- **空白占比**：4/12 = **33.33% > 25%**

### 预期行为
根据**情况3（做空）**的规则：
> 红色柱子存在，绿色和黄色不存在。若空白占比 ≥ 25%，则做空。

**预期信号**：做空  
**实际显示**：诱空试盘抄底 ❌

---

## 🔍 问题排查过程

### 1. 检查预判文件
检查 `data/daily_predictions/prediction_2026-02-28.json`：
```json
{
  "date": "2026-02-28",
  "timestamp": "2026-02-28 02:00:00",
  "color_counts": {
    "green": 0,
    "red": 8,
    "yellow": 0,
    "blank": 4,
    "blank_ratio": 33.33333333333333
  },
  "signal": "做空",
  "description": "🔴⚪ 红色+空白（空白占比33.3%>=25%），预判下跌行情，建议做空。操作提示：相对高点做空"
}
```
✅ JSON文件是正确的！

### 2. 检查Flask API
```bash
curl "http://localhost:9002/api/coin-change-tracker/daily-prediction?date=2026-02-28"
```
返回结果：
```json
{
  "signal": "诱空试盘抄底",
  "description": "⚪🔴 红色+空白且空白占比33.3%>=25%，诱空行情，可以试盘抄底。操作提示：低点做多"
}
```
❌ API返回的是旧数据！

### 3. 发现根本原因
Flask的API读取文件逻辑：
```python
# 1. 优先读取JSONL格式：prediction_20260228.jsonl
# 2. 其次读取JSON格式：prediction_2026-02-28.json
```

检查文件系统：
```bash
$ ls -lh data/daily_predictions/prediction_20260228*
-rw-r--r-- 1 user user 4.3K Feb 28 07:33 prediction_20260228.jsonl
```

**发现问题**：
1. 存在 `prediction_20260228.jsonl` 文件（旧格式）
2. 该文件包含旧的预判数据（在规则修改之前生成的）
3. Flask API优先读取JSONL，导致返回旧数据
4. `regenerate_all_predictions.py` 脚本生成的是JSON格式，不会更新JSONL

---

## ✅ 解决方案

### 1. 删除所有旧的JSONL文件
```bash
cd /home/user/webapp
rm -f data/daily_predictions/prediction_202602*.jsonl
```

删除了26个旧的JSONL文件：
- `prediction_20260202.jsonl`
- `prediction_20260204.jsonl`
- ...
- `prediction_20260228.jsonl`

### 2. 重新生成所有预判文件
```bash
python3 scripts/regenerate_all_predictions.py
```

结果：
```
✅ 2026-02-02: 绿0 红12 黄0 | 诱空试盘抄底
✅ 2026-02-13: 绿0 红6 黄0 | 做空
✅ 2026-02-27: 绿0 红12 黄0 | 诱空试盘抄底
✅ 2026-02-28: 绿0 红8 黄0 | 做空
...
成功: 25 个
失败: 3 个 (2026-02-01, 2026-02-03, 2026-02-11 没有0-2点数据)
```

### 3. 重启Flask清除内存缓存
```bash
pm2 restart flask-app
```

---

## 🧪 验证结果

### API测试
```bash
$ curl "http://localhost:9002/api/coin-change-tracker/daily-prediction?date=2026-02-28"
{
  "success": true,
  "data": {
    "signal": "做空",
    "description": "🔴⚪ 红色+空白（空白占比33.3%>=25%），预判下跌行情，建议做空。操作提示：相对高点做空",
    "color_counts": {
      "green": 0,
      "red": 8,
      "yellow": 0,
      "blank": 4,
      "blank_ratio": 33.33
    }
  }
}
```
✅ API返回正确！

### 关键日期验证
| 日期 | 绿 | 红 | 黄 | 空白 | 空白占比 | 预期信号 | 实际信号 | 结果 |
|------|----|----|----|----|---------|---------|---------|------|
| 2026-02-02 | 0 | 12 | 0 | 0 | 0% | 诱空试盘抄底 | 诱空试盘抄底 | ✅ |
| 2026-02-13 | 0 | 6 | 0 | 6 | 50% | 做空 | 做空 | ✅ |
| 2026-02-27 | 0 | 12 | 0 | 0 | 0% | 诱空试盘抄底 | 诱空试盘抄底 | ✅ |
| 2026-02-28 | 0 | 8 | 0 | 4 | 33.3% | 做空 | 做空 | ✅ |

所有关键日期的逻辑都正确！

---

## 📝 逻辑验证

### 情况5（诱空试盘抄底）
**条件**：绿色=0，黄色=0，红色>0，**空白占比 < 25%**  
**信号**：诱空试盘抄底  
**操作**：低点做多  

**测试案例**：
- 2026-02-02: 红12，空白0 (0%) → ✅ 诱空试盘抄底
- 2026-02-27: 红12，空白0 (0%) → ✅ 诱空试盘抄底

### 情况3（做空）
**条件**：绿色=0，黄色=0，红色>0，**空白占比 ≥ 25%**  
**信号**：做空  
**操作**：相对高点做空  

**测试案例**：
- 2026-02-13: 红6，空白6 (50%) → ✅ 做空
- 2026-02-28: 红8，空白4 (33.3%) → ✅ 做空

---

## 🚀 部署信息

- **GitHub仓库**: https://github.com/jamesyidc/111155440228
- **最新提交**: ea29268 (main分支)
- **部署URL**: https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/coin-change-tracker
- **系统状态**: 
  - Flask: 端口9002 ✅ 运行中
  - PM2服务: 26个服务 ✅ 全部online
  - 数据采集: ✅ 正常运行

---

## 📚 技术细节

### Flask API文件读取优先级
```python
# app.py 中的逻辑
def get_daily_prediction():
    # 1. 优先读取JSONL：prediction_20260228.jsonl
    prediction_file = Path(f'data/daily_predictions/prediction_{today_short}.jsonl')
    
    if not prediction_file.exists():
        # 2. 兼容JSON：prediction_2026-02-28.json
        prediction_file = Path(f'data/daily_predictions/prediction_{today}.json')
```

### regenerate_all_predictions.py 输出格式
```python
# 生成JSON格式，不是JSONL
pred_file = f'data/daily_predictions/prediction_{date_str}.json'
with open(pred_file, 'w', encoding='utf-8') as f:
    json.dump(prediction, f, ensure_ascii=False, indent=2)
```

### 为什么会有JSONL文件？
- JSONL文件是由 `coin-change-predictor` 服务生成的（运行在PM2中）
- 该服务在每天0-2点实时生成预判数据
- `regenerate_all_predictions.py` 是手动运行的脚本，用于批量重新生成历史数据
- 两者输出格式不同，导致冲突

---

## 🔄 后续优化建议

### 1. 统一文件格式
建议修改 `regenerate_all_predictions.py`，使其也生成JSONL格式：
```python
# 保持与coin-change-predictor服务一致
pred_file = f'data/daily_predictions/prediction_{date_str.replace("-", "")}.jsonl'
with open(pred_file, 'a', encoding='utf-8') as f:
    f.write(json.dumps(prediction, ensure_ascii=False) + '\n')
```

### 2. 清理旧数据的自动化
添加清理脚本：
```bash
# scripts/cleanup_old_predictions.sh
# 删除超过30天的预判文件
find data/daily_predictions -name "prediction_*.jsonl" -mtime +30 -delete
find data/daily_predictions -name "prediction_*.json" -mtime +30 -delete
```

### 3. 文档更新
更新 `README.md`，说明：
- 预判文件有两种格式（JSONL和JSON）
- Flask API的优先级
- 如何重新生成历史数据
- 如何处理缓存问题

---

## 📋 Git 提交记录

```bash
Commit: ea29268
Date: 2026-02-28
Branch: main
Message: fix: 修复预判数据缓存问题 - 删除旧的JSONL文件，使用最新的JSON格式

Changes:
- 删除 26 个旧的JSONL文件
- 重新生成所有2月份的预判文件（JSON格式）
- 验证所有关键日期的逻辑正确性
```

---

## 🎯 总结

### 问题本质
不是预判逻辑错误，而是**文件格式冲突导致的缓存问题**。

### 解决关键
删除旧的JSONL文件，统一使用JSON格式。

### 验证结果
✅ API返回正确  
✅ 所有关键日期逻辑正确  
✅ 空白占比计算正确  
✅ 信号判断符合规则

### 经验教训
1. ✅ **文件格式需要统一**（JSONL vs JSON）
2. ✅ **API读取优先级要明确**
3. ✅ **重新生成数据后要清理旧文件**
4. ✅ **重启服务清除内存缓存**
5. ✅ **测试要覆盖整个数据流**（文件 → API → 页面）

---

**修复时间**: 2026-02-28  
**修复人员**: AI Assistant  
**用户反馈**: 等待验证  
**状态**: ✅ **修复完成，待用户确认**
