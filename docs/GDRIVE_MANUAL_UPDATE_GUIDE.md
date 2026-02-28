# Google Drive TXT监控 - 手动更新指南

## 📋 问题现状

- **当前日期**: 2026-02-03（今天）
- **配置日期**: 2026-02-01（过期2天）
- **问题**: 
  1. ❌ 今天的子文件夹ID未获取
  2. ❌ 今天文件夹下的TXT文件列表未获取
  3. ❌ 最新的TXT文件未获取

## 🔧 快速修复方法

### 方法1：使用快速更新脚本（推荐）

#### 步骤1：获取今天文件夹的共享链接

1. 打开Google Drive爷爷文件夹：
   ```
   https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH
   ```

2. 进入 **"首页数据"** 文件夹

3. 找到 **"2026-02-03"** 文件夹

4. 右键点击文件夹 → **"取得链接"**

5. 设置为 **"任何人都可以查看"**

6. **复制链接**

#### 步骤2：运行更新脚本

```bash
cd /home/user/webapp && python3 source_code/quick_update_gdrive.py <你复制的链接>
```

**示例**：
```bash
cd /home/user/webapp && python3 source_code/quick_update_gdrive.py https://drive.google.com/drive/folders/xxxxx
```

或者直接提供文件夹ID：
```bash
cd /home/user/webapp && python3 source_code/quick_update_gdrive.py 文件夹ID
```

### 方法2：通过网页手动配置

访问配置页面：
```
https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/gdrive-config
```

在页面中：
1. 输入今天文件夹的共享链接
2. 点击"更新配置"按钮
3. 系统会自动更新配置

## 📂 文件夹结构

```
爷爷文件夹 (1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH)
└── 首页数据 (父文件夹 - 需要ID)
    ├── 2026-02-01 (过期)
    ├── 2026-02-02 (过期)
    └── 2026-02-03 (今天 - 需要ID) ← 我们需要这个！
        ├── 2026-02-03_0900.txt
        ├── 2026-02-03_1000.txt
        ├── 2026-02-03_1100.txt
        └── ...
```

## 🆘 需要提供的信息

请提供以下**任意一项**信息：

### 选项1：今天文件夹的共享链接 ⭐ 最简单
```
https://drive.google.com/drive/folders/[今天文件夹ID]
```

### 选项2：首页数据文件夹的共享链接
```
https://drive.google.com/drive/folders/[首页数据文件夹ID]
```

### 选项3：直接提供文件夹ID
```
今天文件夹ID: ___________
首页数据文件夹ID: ___________
```

## 🔍 如何获取共享链接

1. **打开Google Drive**
   - 访问：https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH

2. **进入首页数据文件夹**

3. **找到2026-02-03文件夹**

4. **右键点击文件夹**

5. **选择"取得链接" (Get link)**

6. **设置权限为"任何人都可以查看"**
   - Anyone with the link can view

7. **复制链接**

8. **提供给我**

## 📊 更新后的效果

更新成功后，你会看到：

### gdrive-detector页面
```
✅ 检测状态: 已停止
📁 文件时间戳: 2026-02-03 17:00:00  ← 今天的时间
⏰ 数据延迟: 0小时
🔢 检查次数: 15267

📁 双数日最近父文件夹: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
📁 单数日最近父文件夹: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
🆔 父文件夹ID: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
🗂️ 今日文件夹ID: [新的文件夹ID]  ← 会显示今天的ID

📂 今日TXT文件列表:
  • 2026-02-03_0900.txt
  • 2026-02-03_1000.txt
  • ...
```

## 🛠️ 可用的脚本

### 1. quick_update_gdrive.py（推荐）
**位置**: `/home/user/webapp/source_code/quick_update_gdrive.py`

**用途**: 快速更新，直接指定今天的文件夹ID或链接

**使用**:
```bash
python3 source_code/quick_update_gdrive.py <今天文件夹链接>
```

### 2. manual_update_gdrive_today.py
**位置**: `/home/user/webapp/source_code/manual_update_gdrive_today.py`

**用途**: 从首页数据文件夹自动查找今天的子文件夹

**使用**:
```bash
python3 source_code/manual_update_gdrive_today.py <首页数据文件夹ID>
```

### 3. update_gdrive_config_from_grandparent.py
**位置**: `/home/user/webapp/source_code/update_gdrive_config_from_grandparent.py`

**用途**: 从爷爷文件夹开始查找（需要完整的访问权限）

**使用**:
```bash
python3 source_code/update_gdrive_config_from_grandparent.py
```

## ⚡ 一键修复命令

如果你已经有了今天文件夹的链接，可以直接执行：

```bash
# 替换 YOUR_FOLDER_LINK 为你的链接
cd /home/user/webapp && python3 source_code/quick_update_gdrive.py YOUR_FOLDER_LINK
```

## 📞 需要帮助？

如果遇到问题，请提供：
1. 今天文件夹的共享链接
2. 或者截图显示你能看到的文件夹结构

---

**生成时间**: 2026-02-03 17:45:00  
**状态**: 等待用户提供今天文件夹的共享链接  
**优先级**: 🔴 高
