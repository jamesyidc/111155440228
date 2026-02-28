# 爆仓标记持久化修复报告 2026-02-28

## 📋 问题描述

用户反馈：重新部署后，在爆仓月线图页面设置的做多/做空标记会消失。

## 🔍 问题诊断

### 原始实现分析
1. **前端实现**：标记仅保存在浏览器的localStorage中
2. **存储位置**：`localStorage.setItem('liquidation_marks', ...)`
3. **问题影响**：
   - 标记只在本地浏览器可见
   - 更换浏览器或设备后标记消失
   - 清除浏览器缓存会丢失所有标记
   - 重新部署时如果URL变化（sandbox ID变化），标记会丢失

### 后端API问题
虽然前端代码已经实现了服务器端持久化逻辑，但发现API无法访问：

```bash
curl http://localhost:9002/api/liquidation/marks
# 返回 404 Not Found
```

#### 根本原因
API路由定义在 `if __name__ == '__main__'` 块内部：

```python
# app.py 第28128-28199行（修复前）
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9002, debug=False)

@app.route('/api/liquidation/marks', methods=['GET'])  # ❌ 这里定义路由
def api_liquidation_marks_get():
    ...

@app.route('/api/liquidation/marks', methods=['POST'])
def api_liquidation_marks_save():
    ...
```

**问题分析**：
- 当通过 `pm2 start app.py` 运行时，Python模块被导入而不是直接执行
- `if __name__ == '__main__'` 条件不满足
- 块内的代码（包括路由定义）不会被执行
- Flask应用启动但没有这些路由，导致404错误

## 🔧 修复方案

### 1. 后端API修复

#### 修复1：移动路由定义位置
将路由定义从main块移到全局作用域：

```python
# app.py 修复后
@app.route('/api/liquidation/marks', methods=['GET'])
def api_liquidation_marks_get():
    """获取爆仓月线图的所有标记"""
    try:
        import json
        from pathlib import Path
        
        marks_file = Path('/home/user/webapp/data/liquidation_marks.json')
        
        if marks_file.exists():
            with open(marks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 兼容新旧格式
                if isinstance(data, dict) and 'marks' in data:
                    marks = data['marks']
                else:
                    marks = data
        else:
            marks = []
        
        return jsonify({
            'success': True,
            'marks': marks,
            'count': len(marks)
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/liquidation/marks', methods=['POST'])
def api_liquidation_marks_save():
    """保存爆仓月线图的标记"""
    try:
        import json
        from pathlib import Path
        from datetime import datetime
        
        data = request.get_json()
        marks = data.get('marks', [])
        
        marks_file = Path('/home/user/webapp/data/liquidation_marks.json')
        marks_file.parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            'marks': marks,
            'last_updated': datetime.now().isoformat(),
            'count': len(marks)
        }
        
        with open(marks_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'已保存 {len(marks)} 个标记',
            'count': len(marks)
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9002, debug=False)
```

#### 修复2：数据格式兼容性
修复GET接口，正确处理保存的数据格式：
- 保存时：包含 `marks`、`last_updated`、`count` 的对象
- 读取时：提取 `marks` 数组返回

### 2. 前端实现（已存在）

前端代码已经实现了双重保存机制：

```javascript
// templates/liquidation_monthly.html
async function saveMarksToStorage() {
    const marks = chartData
        .map((item, index) => ({
            time: item.time,
            markType: item.markType
        }))
        .filter(m => m.markType);
    
    // 1. 保存到localStorage（本地备份）
    localStorage.setItem('liquidation_marks', JSON.stringify(marks));
    
    // 2. 保存到服务器（永久存储）✅
    try {
        const response = await fetch('/api/liquidation/marks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                marks: marks
            })
        });
        
        const result = await response.json();
        if (result.success) {
            console.log(`✅ 已保存 ${marks.length} 个标记到服务器`);
        } else {
            console.error('❌ 保存到服务器失败:', result.error);
        }
    } catch (error) {
        console.error('❌ 保存到服务器异常:', error);
    }
}

async function loadMarksFromStorage() {
    try {
        // 优先从服务器加载 ✅
        const response = await fetch('/api/liquidation/marks');
        const result = await response.json();
        
        if (result.success && result.marks) {
            let marks = result.marks;
            
            // 兼容新格式
            if (marks.marks) {
                marks = marks.marks;
            }
            
            marks.forEach(mark => {
                const item = chartData.find(d => d.time === mark.time);
                if (item) {
                    item.markType = mark.markType;
                }
            });
            console.log(`✅ 从服务器加载了 ${marks.length} 个标记`);
            return;
        }
    } catch (error) {
        console.warn('⚠️ 从服务器加载标记失败，尝试从本地加载:', error);
    }
    
    // 服务器加载失败，从localStorage加载
    try {
        const saved = localStorage.getItem('liquidation_marks');
        if (saved) {
            const marks = JSON.parse(saved);
            marks.forEach(mark => {
                const item = chartData.find(d => d.time === mark.time);
                if (item) {
                    item.markType = mark.markType;
                }
            });
            console.log(`✅ 从本地缓存加载了 ${marks.length} 个标记`);
        }
    } catch (e) {
        console.error('❌ 加载标记失败:', e);
    }
}
```

## ✅ 修复验证

### API测试

1. **GET接口测试**：
```bash
curl -s http://localhost:9002/api/liquidation/marks | python3 -m json.tool
```
结果：
```json
{
    "count": 2,
    "marks": [
        {
            "markType": "long",
            "time": "2026-02-28 10:00"
        },
        {
            "markType": "short",
            "time": "2026-02-28 12:00"
        }
    ],
    "success": true
}
```
✅ **测试通过**

2. **POST接口测试**：
```bash
curl -X POST http://localhost:9002/api/liquidation/marks \
  -H "Content-Type: application/json" \
  -d '{"marks":[{"time":"2026-02-28 10:00","markType":"long"}]}'
```
结果：
```json
{
    "count": 1,
    "message": "已保存 1 个标记",
    "success": true
}
```
✅ **测试通过**

3. **数据文件验证**：
```bash
cat data/liquidation_marks.json
```
结果：
```json
{
  "marks": [
    {
      "time": "2026-02-28 10:00",
      "markType": "long"
    },
    {
      "time": "2026-02-28 12:00",
      "markType": "short"
    }
  ],
  "last_updated": "2026-02-28T12:43:11.478999",
  "count": 2
}
```
✅ **数据正确保存**

## 📊 功能特性

### 1. 双重保存机制
- **localStorage**：本地快速访问，临时备份
- **服务器端**：永久存储，跨设备同步

### 2. 优先级策略
- 加载时优先从服务器读取
- 服务器失败时回退到localStorage
- 保存时同时更新两者

### 3. 数据安全
- 服务器数据带时间戳
- 保存失败不影响现有标记
- 自动创建数据目录

### 4. 兼容性
- 兼容旧的localStorage数据
- 兼容新旧数据格式
- 平滑迁移无需手动操作

## 🚀 部署信息

- **提交哈希**：688f023
- **GitHub仓库**：https://github.com/jamesyidc/111155440228
- **分支**：main
- **部署URL**：https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/liquidation-monthly
- **Flask端口**：9002
- **PM2状态**：26个服务全部online

### 相关文件
- `app.py`：后端API路由（第28127-28199行）
- `templates/liquidation_monthly.html`：前端标记逻辑（第893-972行）
- `data/liquidation_marks.json`：标记存储文件

## 📝 技术经验教训

### Python Flask路由定义位置
**错误示例**：
```python
if __name__ == '__main__':
    app.run(...)

@app.route('/api/...')  # ❌ 通过PM2启动时不会执行
def handler():
    ...
```

**正确示例**：
```python
@app.route('/api/...')  # ✅ 在全局作用域定义
def handler():
    ...

if __name__ == '__main__':
    app.run(...)
```

### PM2与Flask的差异
- **直接运行**：`python app.py` → `__name__ == '__main__'` 为True
- **PM2运行**：`pm2 start app.py` → 模块被导入，`__name__ == 'app'`
- **结果**：main块内的代码在PM2模式下不会执行

## 🎯 用户影响

### 修复前
- ❌ 标记只在当前浏览器可见
- ❌ 更换设备/浏览器后标记丢失
- ❌ 重新部署后标记消失
- ❌ 清除缓存会丢失所有设置

### 修复后
- ✅ 标记永久保存在服务器
- ✅ 跨浏览器/设备同步
- ✅ 重新部署后标记保留
- ✅ 清除缓存不影响服务器数据

## 📅 修复时间线

- **2026-02-28 12:35**：用户报告问题
- **2026-02-28 12:40**：诊断发现API返回404
- **2026-02-28 12:41**：定位路由定义位置错误
- **2026-02-28 12:42**：修复路由位置
- **2026-02-28 12:43**：API测试通过
- **2026-02-28 12:44**：提交修复并推送
- **2026-02-28 12:45**：生成修复文档

## 🔮 未来改进建议

1. **数据备份**：定期备份 `liquidation_marks.json`
2. **版本管理**：在数据文件中添加版本号
3. **用户多账户**：支持多用户各自的标记
4. **历史记录**：保存标记修改历史
5. **导入导出**：支持标记数据导入导出

---

**修复完成** ✅ 
**问题解决** ✅ 
**文档归档** ✅
