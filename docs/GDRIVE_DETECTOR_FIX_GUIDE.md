# 🔧 Google Drive监控系统 - 配置修复指南

## 📋 问题说明
**报告时间**: 2026-02-03 17:50:00  
**页面**: Google Drive TXT监控  
**链接**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/gdrive-detector

### **问题现象**
- ❌ 配置文件过期（停留在2026-02-01）
- ❌ 无法自动找到今天日期的文件夹
- ❌ TXT文件监控失效

---

## ✅ 解决方案

### **方案1: 提供"首页数据"文件夹的共享链接** ⭐推荐

#### 步骤：
1. 打开爷爷文件夹：https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH
2. 找到"首页数据"文件夹
3. 右键点击"首页数据"文件夹 → 获取链接
4. 复制共享链接（格式：`https://drive.google.com/drive/folders/FOLDER_ID`）
5. 将链接提供给我

#### 示例链接格式：
```
https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
```

---

### **方案2: 直接提供今天日期文件夹的共享链接**

#### 步骤：
1. 打开爷爷文件夹
2. 进入"首页数据"文件夹
3. 找到今天日期的文件夹（2026-02-03）
4. 右键点击今天日期文件夹 → 获取链接
5. 将链接提供给我

---

## 🔍 当前配置状态

### **配置文件位置**
```bash
/home/user/webapp/daily_folder_config.json
```

### **当前配置内容**
```json
{
  "root_folder_odd": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
  "root_folder_even": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
  "current_date": "2026-02-01",  ❌ 过期
  "folder_id": "1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0",  ❌ 2月1日的文件夹
  ...
}
```

### **需要的配置**
```json
{
  "grandparent_folder_id": "1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH",
  "parent_folder_id": "【首页数据文件夹ID】",
  "current_date": "2026-02-03",
  "folder_id": "【2026-02-03文件夹ID】",
  ...
}
```

---

## 📂 文件夹结构

```
爷爷文件夹 (1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH)
  │
  ├─ 首页数据 (需要获取此文件夹ID)
  │   │
  │   ├─ 2026-02-01 (旧的)
  │   ├─ 2026-02-02 (旧的)
  │   └─ 2026-02-03 (今天，需要获取此文件夹ID)
  │       │
  │       ├─ 2026-02-03_0900.txt
  │       ├─ 2026-02-03_1000.txt
  │       └─ ...
  │
  └─ 其他文件夹...
```

---

## 🛠️ 技术说明

### **为什么需要这些信息？**

1. **爷爷文件夹** → 已有 ✅
   - ID: `1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH`
   - 用途: 最顶层的文件夹

2. **首页数据文件夹** → 需要 ❌
   - ID: `未知`
   - 用途: 包含所有日期文件夹的父文件夹

3. **今天日期文件夹** → 需要 ❌
   - ID: `未知`
   - 格式: `2026-02-03`
   - 用途: 包含今天的TXT文件

### **Google Drive API限制**

- ❌ `embeddedfolderview` 端点不再返回文件夹内容
- ❌ 直接访问文件夹URL返回完整的HTML页面，无法解析
- ✅ 需要使用共享链接或Google Drive API v3

---

## 📝 临时手动修复方法

如果您能提供以下任一信息，我可以立即修复：

### 选项1️⃣: "首页数据"文件夹的共享链接
```
https://drive.google.com/drive/folders/[FOLDER_ID]
```

### 选项2️⃣: 今天日期文件夹的共享链接
```
https://drive.google.com/drive/folders/[FOLDER_ID]
```

### 选项3️⃣: 直接提供两个文件夹ID
```
首页数据文件夹ID: [ID]
2026-02-03文件夹ID: [ID]
```

---

## 🔄 自动更新机制

一旦配置正确后，系统将：

1. ✅ 每天自动检查今天日期的文件夹
2. ✅ 自动更新配置文件
3. ✅ 监控TXT文件的更新
4. ✅ 根据单双数日期自动切换父文件夹

---

## ⚠️ 注意事项

1. 确保所有文件夹都已设置为"任何人都可以查看"
2. 共享链接格式必须是 `https://drive.google.com/drive/folders/[ID]`
3. 文件夹命名必须严格按照 `YYYY-MM-DD` 格式（例如：2026-02-03）
4. TXT文件命名必须严格按照 `YYYY-MM-DD_HHMM.txt` 格式

---

## 📞 下一步

**请提供以下任一信息：**

1. "首页数据"文件夹的共享链接 ⭐推荐
2. 或 2026-02-03 文件夹的共享链接
3. 或 两个文件夹的ID

**获取共享链接的步骤：**
1. 在Google Drive中找到文件夹
2. 右键点击文件夹
3. 选择"获取链接"或"共享"
4. 设置为"任何人都可以查看"
5. 复制链接

---
**创建时间**: 2026-02-03 17:50:00  
**状态**: 等待用户提供文件夹信息  
**作者**: Claude AI Assistant
