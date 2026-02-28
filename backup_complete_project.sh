#!/bin/bash
# 完整项目备份脚本
# 创建时间: 2026-02-27
# 备份范围: 全部数据和代码（不含日志和临时文件）

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 开始完整项目备份"
echo "=========================================="
echo ""

# 定义变量
PROJECT_DIR="/home/user/webapp"
BACKUP_DIR="/tmp"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="webapp_complete_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

echo "📦 备份配置："
echo "  - 项目目录: ${PROJECT_DIR}"
echo "  - 备份目录: ${BACKUP_DIR}"
echo "  - 备份文件: ${BACKUP_FILE}"
echo ""

# 创建临时备份目录
echo "📁 创建临时备份目录..."
mkdir -p "${BACKUP_PATH}"

cd "${PROJECT_DIR}"

# ==================== 1. Python应用文件 ====================
echo ""
echo "============================================"
echo "📄 1. 备份 Python 应用文件"
echo "============================================"

echo "  ✓ 复制 app.py (主应用)"
cp -v app.py "${BACKUP_PATH}/"

echo "  ✓ 复制根目录 Python 文件"
find . -maxdepth 1 -name "*.py" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

# ==================== 2. 源代码目录 ====================
echo ""
echo "============================================"
echo "💻 2. 备份源代码目录"
echo "============================================"

echo "  ✓ 复制 source_code/ (700KB)"
if [ -d "source_code" ]; then
    cp -rv source_code "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 panic_paged_v2/ (140KB)"
if [ -d "panic_paged_v2" ]; then
    cp -rv panic_paged_v2 "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 panic_v3/ (168KB)"
if [ -d "panic_v3" ]; then
    cp -rv panic_v3 "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 code/ (956KB)"
if [ -d "code" ]; then
    cp -rv code "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 monitors/ (180KB)"
if [ -d "monitors" ]; then
    cp -rv monitors "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 scripts/ (244KB)"
if [ -d "scripts" ]; then
    cp -rv scripts "${BACKUP_PATH}/"
fi

# ==================== 3. 采集器和服务 ====================
echo ""
echo "============================================"
echo "🔄 3. 备份采集器和服务文件"
echo "============================================"

# 采集器文件
echo "  ✓ 复制所有采集器文件 (*collector.py)"
find . -maxdepth 1 -name "*collector*.py" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

# 监控器文件
echo "  ✓ 复制所有监控器文件 (*monitor*.py)"
find . -maxdepth 1 -name "*monitor*.py" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

# 管理器文件
echo "  ✓ 复制所有管理器文件 (*manager*.py)"
find . -maxdepth 1 -name "*manager*.py" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

# ==================== 4. 配置文件 ====================
echo ""
echo "============================================"
echo "⚙️  4. 备份配置文件"
echo "============================================"

echo "  ✓ 复制 config/ 目录"
if [ -d "config" ]; then
    cp -rv config "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 requirements.txt"
[ -f "requirements.txt" ] && cp -v requirements.txt "${BACKUP_PATH}/"

echo "  ✓ 复制 package.json"
[ -f "package.json" ] && cp -v package.json "${BACKUP_PATH}/"

echo "  ✓ 复制 ecosystem.config.js"
[ -f "ecosystem.config.js" ] && cp -v ecosystem.config.js "${BACKUP_PATH}/"

# ==================== 5. PM2 配置 ====================
echo ""
echo "============================================"
echo "🔧 5. 备份 PM2 配置"
echo "============================================"

echo "  ✓ 导出 PM2 进程列表"
pm2 jlist > "${BACKUP_PATH}/pm2_processes.json" 2>/dev/null || echo "    ⚠️  PM2 未运行"

echo "  ✓ 导出 PM2 配置"
pm2 save --force 2>/dev/null || echo "    ⚠️  PM2 未运行"

if [ -d "${HOME}/.pm2" ]; then
    echo "  ✓ 复制 PM2 配置目录"
    mkdir -p "${BACKUP_PATH}/pm2_config"
    cp -v "${HOME}/.pm2/dump.pm2" "${BACKUP_PATH}/pm2_config/" 2>/dev/null || true
fi

# ==================== 6. Web 前端文件 ====================
echo ""
echo "============================================"
echo "🌐 6. 备份 Web 前端文件"
echo "============================================"

echo "  ✓ 复制 templates/ (7.3MB)"
if [ -d "templates" ]; then
    cp -rv templates "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 static/ (384KB)"
if [ -d "static" ]; then
    cp -rv static "${BACKUP_PATH}/"
fi

# ==================== 7. 文档 ====================
echo ""
echo "============================================"
echo "📚 7. 备份文档"
echo "============================================"

echo "  ✓ 复制 docs/ (8.1MB)"
if [ -d "docs" ]; then
    cp -rv docs "${BACKUP_PATH}/"
fi

echo "  ✓ 复制 README 文件"
find . -maxdepth 1 -name "README*" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

echo "  ✓ 复制 Markdown 文档"
find . -maxdepth 1 -name "*.md" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

# ==================== 8. 数据文件（全部数据）====================
echo ""
echo "============================================"
echo "💾 8. 备份数据文件（全部数据，约3GB）"
echo "============================================"
echo "  ⚠️  这将需要较长时间，请耐心等待..."
echo ""

if [ -d "data" ]; then
    echo "  📊 正在备份 data/ 目录..."
    
    # 创建data目录
    mkdir -p "${BACKUP_PATH}/data"
    
    # 统计文件数量
    TOTAL_FILES=$(find data -type f | wc -l)
    echo "  📈 总文件数: ${TOTAL_FILES}"
    
    # 使用tar进行增量复制，显示进度
    echo "  🔄 开始复制..."
    tar cf - data | pv -s $(du -sb data | awk '{print $1}') | tar xf - -C "${BACKUP_PATH}/"
    
    echo "  ✅ 数据目录备份完成"
fi

# ==================== 9. 测试文件 ====================
echo ""
echo "============================================"
echo "🧪 9. 备份测试文件"
echo "============================================"

if [ -d "tests" ]; then
    echo "  ✓ 复制 tests/ 目录"
    cp -rv tests "${BACKUP_PATH}/"
fi

echo "  ✓ 复制测试脚本"
find . -maxdepth 1 -name "test_*.py" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

# ==================== 10. Shell 脚本 ====================
echo ""
echo "============================================"
echo "🔨 10. 备份 Shell 脚本"
echo "============================================"

echo "  ✓ 复制所有 .sh 文件"
find . -maxdepth 1 -name "*.sh" -type f -exec cp -v {} "${BACKUP_PATH}/" \;

# ==================== 11. Git 信息 ====================
echo ""
echo "============================================"
echo "🌿 11. 备份 Git 信息"
echo "============================================"

if [ -d ".git" ]; then
    echo "  ✓ 导出 Git 信息"
    git log --oneline -50 > "${BACKUP_PATH}/git_recent_commits.txt" 2>/dev/null || true
    git status > "${BACKUP_PATH}/git_status.txt" 2>/dev/null || true
    git branch -a > "${BACKUP_PATH}/git_branches.txt" 2>/dev/null || true
    git remote -v > "${BACKUP_PATH}/git_remotes.txt" 2>/dev/null || true
    
    echo "  ⚠️  注意: .git 目录未包含在备份中"
    echo "  💡 建议: 使用 git clone 从远程仓库恢复"
fi

# ==================== 12. 系统信息 ====================
echo ""
echo "============================================"
echo "🖥️  12. 收集系统信息"
echo "============================================"

mkdir -p "${BACKUP_PATH}/system_info"

echo "  ✓ Python 版本"
python3 --version > "${BACKUP_PATH}/system_info/python_version.txt" 2>&1

echo "  ✓ Python 包列表"
pip list > "${BACKUP_PATH}/system_info/pip_list.txt" 2>&1

echo "  ✓ Node.js 版本"
node --version > "${BACKUP_PATH}/system_info/node_version.txt" 2>&1

echo "  ✓ npm 版本"
npm --version > "${BACKUP_PATH}/system_info/npm_version.txt" 2>&1

echo "  ✓ PM2 版本"
pm2 --version > "${BACKUP_PATH}/system_info/pm2_version.txt" 2>&1

echo "  ✓ 系统信息"
uname -a > "${BACKUP_PATH}/system_info/system_uname.txt"

echo "  ✓ 磁盘使用情况"
df -h > "${BACKUP_PATH}/system_info/disk_usage.txt"

echo "  ✓ 环境变量"
env | sort > "${BACKUP_PATH}/system_info/env_variables.txt"

# ==================== 13. 创建备份元数据 ====================
echo ""
echo "============================================"
echo "📋 13. 创建备份元数据"
echo "============================================"

cat > "${BACKUP_PATH}/BACKUP_INFO.txt" << EOF
========================================
完整项目备份信息
========================================

备份时间: ${TIMESTAMP}
备份名称: ${BACKUP_NAME}
原始路径: ${PROJECT_DIR}

========================================
备份内容概览
========================================

✅ Python 应用文件
   - app.py (主Flask应用)
   - 根目录所有 .py 文件

✅ 源代码目录
   - source_code/ (700KB) - 核心API代码
   - panic_paged_v2/ (140KB) - 爆仓分页系统v2
   - panic_v3/ (168KB) - 爆仓系统v3
   - code/ (956KB) - 通用代码库
   - monitors/ (180KB) - 监控脚本
   - scripts/ (244KB) - 工具脚本

✅ 配置文件
   - config/ - 所有配置文件
   - requirements.txt - Python依赖
   - package.json - Node.js依赖
   - ecosystem.config.js - PM2配置

✅ PM2 配置
   - pm2_processes.json - 进程列表
   - pm2_config/ - PM2配置文件

✅ Web 前端
   - templates/ (7.3MB) - HTML模板
   - static/ (384KB) - 静态资源

✅ 文档
   - docs/ (8.1MB) - 所有文档
   - README 和 Markdown 文件

✅ 数据文件
   - data/ (~3GB) - 完整数据
   - 包含所有历史数据，非7天数据

✅ 测试文件
   - tests/ - 测试代码
   - test_*.py - 测试脚本

✅ Shell 脚本
   - 所有 .sh 文件

✅ Git 信息
   - 最近50次提交记录
   - 当前状态
   - 分支信息
   - 远程仓库信息

✅ 系统信息
   - Python/Node.js/PM2 版本
   - pip/npm 包列表
   - 系统环境信息

========================================
排除内容（未备份）
========================================

❌ logs/ - 日志文件（65MB）
❌ node_modules/ - Node.js依赖（34MB）
❌ backups/ - 旧备份目录
❌ __pycache__/ - Python缓存
❌ .git/ - Git仓库（建议从远程克隆）
❌ *.pyc - Python编译文件
❌ .DS_Store - 系统文件

========================================
文件统计
========================================

总文件数: $(find "${BACKUP_PATH}" -type f | wc -l)
总目录数: $(find "${BACKUP_PATH}" -type d | wc -l)
总大小: $(du -sh "${BACKUP_PATH}" | awk '{print $1}')

========================================
恢复说明
========================================

1. 解压备份文件:
   tar -xzf ${BACKUP_NAME}.tar.gz

2. 查看详细恢复说明:
   cat ${BACKUP_NAME}/DEPLOYMENT_GUIDE.md

3. 运行恢复脚本:
   bash ${BACKUP_NAME}/restore_project.sh

========================================
重要提示
========================================

⚠️  此备份包含全部数据（约3GB），不是7天数据
⚠️  恢复前请先安装所有系统依赖
⚠️  建议在相同或更高版本的系统上恢复
⚠️  Telegram等敏感配置请单独管理

========================================
备份完成时间: $(date)
========================================
EOF

echo "  ✅ 备份元数据已创建"

# ==================== 14. 压缩备份 ====================
echo ""
echo "============================================"
echo "📦 14. 压缩备份文件"
echo "============================================"
echo "  ⏳ 正在压缩，请耐心等待..."
echo ""

cd "${BACKUP_DIR}"

# 使用 tar 和 gzip 压缩，显示进度
tar czf "${BACKUP_FILE}" "${BACKUP_NAME}" --checkpoint=10000 --checkpoint-action=echo="%T"

echo ""
echo "  ✅ 压缩完成"

# 删除临时目录
rm -rf "${BACKUP_PATH}"

# ==================== 15. 生成校验和 ====================
echo ""
echo "============================================"
echo "🔐 15. 生成校验和"
echo "============================================"

CHECKSUM=$(md5sum "${BACKUP_FILE}" | awk '{print $1}')
echo "${CHECKSUM}  ${BACKUP_FILE}" > "${BACKUP_FILE}.md5"
echo "  ✓ MD5: ${CHECKSUM}"

# ==================== 完成 ====================
echo ""
echo "=========================================="
echo "✅ 备份完成！"
echo "=========================================="
echo ""
echo "📦 备份文件信息:"
echo "  - 文件路径: ${BACKUP_FILE}"
echo "  - 文件大小: $(du -h "${BACKUP_FILE}" | awk '{print $1}')"
echo "  - MD5校验: ${CHECKSUM}"
echo ""
echo "📋 下一步操作:"
echo "  1. 下载备份文件: ${BACKUP_FILE}"
echo "  2. 验证MD5校验值"
echo "  3. 保存到安全位置"
echo ""
echo "🔄 恢复方法:"
echo "  tar -xzf ${BACKUP_NAME}.tar.gz"
echo "  cd ${BACKUP_NAME}"
echo "  cat DEPLOYMENT_GUIDE.md"
echo ""
echo "=========================================="
