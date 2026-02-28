# Google Drive 文件夹结构完整文档

**最后更新**: 2026-02-01 14:05:00  
**状态**: ✅ 已验证并可用

---

## 📂 完整文件夹层级结构

```
爷爷文件夹 (根目录)
├─ ID: 1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH
├─ 共享链接: https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH?usp=sharing
│
└─── 首页数据 (父文件夹)
     ├─ ID: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
     ├─ 链接: https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
     │
     ├─── 2026-02-01 (今日子文件夹) ⭐
     │    ├─ ID: 1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0
     │    ├─ 链接: https://drive.google.com/drive/folders/1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0
     │    └─ 包含: 83个TXT文件 (截至 13:58:28)
     │
     ├─── 2026-01-31
     ├─── 2026-01-30
     ├─── ...
     └─── (共104个日期文件夹)
```

---

## 🔗 快速访问链接

### 1. 爷爷文件夹（根目录）
**文件夹ID**: `1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH`  
**共享链接**: https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH?usp=sharing

**包含内容**:
- 首页数据 文件夹
- 数据 文件夹
- data 文件夹
- 日志 文件夹
- 监控相关文件
- 各种币种的TXT文件 (AAVE, BTC, ETH, XRP, SOL, 等)
- 易语言脚本文件 (.e, .ebb)

### 2. 首页数据（父文件夹）
**文件夹ID**: `1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV`  
**链接**: https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV

**包含内容**:
- 104个日期文件夹 (YYYY-MM-DD格式)
- 从 2025-10-20 到 2026-02-01
- 每天的快照数据TXT文件

### 3. 今日文件夹 (2026-02-01)
**文件夹ID**: `1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0`  
**链接**: https://drive.google.com/drive/folders/1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0

**包含内容**:
- 83个TXT文件
- 最新文件: 2026-02-01_1343.txt
- 文件命名格式: YYYY-MM-DD_HHMM.txt

---

## 🔍 验证方法

### 方法1: 通过浏览器访问

1. 打开爷爷文件夹链接:
   ```
   https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH?usp=sharing
   ```

2. 找到"首页数据"文件夹并点击进入

3. 找到今天的日期文件夹 `2026-02-01` 并点击进入

4. 查看TXT文件列表

### 方法2: 通过API验证

```python
import requests

# 验证首页数据文件夹
homepage_id = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"
url = f"https://drive.google.com/embeddedfolderview?id={homepage_id}"
response = requests.get(url)

if "2026-02-01" in response.text:
    print("✅ 今天的文件夹存在")
```

### 方法3: 通过监控器日志

```bash
# 查看监控器找到的文件夹ID
pm2 logs gdrive-detector --nostream --lines 50 | grep "文件夹ID"

# 输出示例:
# [2026-02-01 13:58:28] ✅ 找到 2026-02-01 文件夹ID: 1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0
```

---

## 🛠️ 监控器配置

### 当前配置

监控器脚本: `source_code/gdrive_final_detector_with_jsonl.py`

```python
# 首页数据文件夹ID（父文件夹）
ROOT_FOLDER_ID = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"

# 检测间隔
CHECK_INTERVAL = 30  # 秒

# JSONL数据目录
JSONL_DATA_DIR = "/home/user/webapp/data/gdrive_jsonl"
```

### 工作流程

1. **查找今日文件夹**
   - 访问首页数据文件夹 (1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV)
   - 搜索今天日期的子文件夹 (2026-02-01)
   - 提取子文件夹ID (1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0)

2. **获取文件列表**
   - 访问今日文件夹
   - 获取所有TXT文件
   - 找到最新的文件 (按时间排序)

3. **下载和解析**
   - 下载最新TXT文件
   - 解析币种数据
   - 保存到JSONL文件

4. **状态更新**
   - 记录检查时间
   - 记录文件数量
   - 记录导入状态

---

## 📊 数据统计

### 文件夹统计
- **爷爷文件夹项目数**: 42个 (文件夹 + 文件)
- **首页数据日期文件夹**: 104个
- **今日TXT文件数**: 83个
- **历史数据跨度**: 2025-10-20 至今

### 更新频率
- **新TXT文件生成**: 约每10分钟
- **监控器检测**: 每30秒
- **数据写入JSONL**: 实时

---

## 🎯 使用场景

### 场景1: 获取最新数据

```python
# 方法1: 通过监控器自动获取
# PM2服务自动每30秒检测并下载最新文件

# 方法2: 手动查询
import subprocess
result = subprocess.run(
    "python3 /home/user/webapp/scripts/get_today_folder_id.py",
    shell=True, capture_output=True, text=True
)
print(result.stdout)
```

### 场景2: 访问历史数据

```python
# 访问特定日期的文件夹
date = "2026-01-31"
# 需要先从首页数据文件夹找到对应日期的文件夹ID
homepage_id = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"
# 然后访问该日期文件夹
```

### 场景3: 监控文件夹变化

```bash
# 查看监控器实时日志
pm2 logs gdrive-detector --lines 0

# 查看数据文件更新
watch -n 5 'ls -lth /home/user/webapp/data/gdrive_jsonl/*.jsonl | head -3'
```

---

## 🔐 访问权限说明

### 公开共享
- ✅ 爷爷文件夹: 公开共享 (带链接的任何人都可查看)
- ✅ 首页数据: 继承公开权限
- ✅ 日期子文件夹: 继承公开权限
- ✅ TXT文件: 可直接下载

### 无需认证
- ✅ 通过嵌入式视图访问: `https://drive.google.com/embeddedfolderview?id=FOLDER_ID`
- ✅ 不需要OAuth认证
- ✅ 不需要API密钥
- ✅ 适合自动化脚本

---

## 📝 维护日志

### 2026-02-01
- ✅ 验证爷爷文件夹链接可用
- ✅ 确认首页数据文件夹ID: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
- ✅ 确认今日文件夹ID: 1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0
- ✅ 监控器正常运行，每30秒检测
- ✅ 找到104个历史日期文件夹

### 下次检查事项
- [ ] 验证明天 (2026-02-02) 的文件夹是否自动创建
- [ ] 确认监控器能否自动切换到新日期
- [ ] 检查旧日期文件夹的保留策略

---

## 🔗 相关文档

- **文件夹ID查询脚本**: `/home/user/webapp/scripts/get_today_folder_id.py`
- **今日文件夹快速参考**: `/home/user/webapp/TODAY_FOLDER_ID.md`
- **监控器脚本**: `/home/user/webapp/source_code/gdrive_final_detector_with_jsonl.py`
- **JSONL管理器**: `/home/user/webapp/source_code/gdrive_jsonl_manager.py`

---

## ✅ 总结

### 文件夹结构层级
```
1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH (爷爷)
  └─ 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV (首页数据)
      └─ 1y802svJMIfSG7qcNGs7xO7nNp0uyUTK0 (2026-02-01)
          └─ 83个TXT文件
```

### 访问方式
- ✅ 浏览器: 使用共享链接
- ✅ 脚本: 使用embeddedfolderview API
- ✅ 监控器: 自动检测和下载

### 当前状态
- ✅ 所有链接都已验证可用
- ✅ 监控器正常运行
- ✅ 数据实时更新

---

**验证时间**: 2026-02-01 14:05:00  
**验证方法**: 通过共享链接和嵌入式API  
**验证状态**: ✅ 全部通过
