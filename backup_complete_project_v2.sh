#!/bin/bash

# ============================================================
# 完整项目备份脚本 v2.0
# ============================================================
# 功能：备份整个Flask应用到 /tmp 目录，包括所有源码、配置、数据
# 作者：GenSpark AI Developer
# 日期：2026-02-27
# ============================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp"
PROJECT_DIR="/home/user/webapp"
BACKUP_NAME="webapp_complete_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   完整项目备份工具 v2.0${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${GREEN}📦 备份配置：${NC}"
echo -e "  源目录: ${PROJECT_DIR}"
echo -e "  目标目录: ${BACKUP_PATH}"
echo -e "  备份文件: ${BACKUP_PATH}.tar.gz"
echo ""

# 创建临时备份目录
echo -e "${YELLOW}[1/6] 创建临时备份目录...${NC}"
mkdir -p "${BACKUP_PATH}"

# 备份主要源码和配置文件
echo -e "${YELLOW}[2/6] 备份主要源码和配置文件...${NC}"
cd "${PROJECT_DIR}"

# 复制主应用文件
echo "  ✓ 复制 app.py"
cp app.py "${BACKUP_PATH}/"

# 复制所有根目录Python文件
echo "  ✓ 复制根目录Python文件"
find . -maxdepth 1 -name "*.py" -exec cp {} "${BACKUP_PATH}/" \;

# 复制所有Shell脚本
echo "  ✓ 复制Shell脚本"
find . -maxdepth 1 -name "*.sh" -exec cp {} "${BACKUP_PATH}/" \;

# 复制配置文件
echo "  ✓ 复制配置文件"
find . -maxdepth 1 -name "*.json" -exec cp {} "${BACKUP_PATH}/" \;
cp .env "${BACKUP_PATH}/" 2>/dev/null || echo "    ⚠ .env 不存在"
cp .gitignore "${BACKUP_PATH}/" 2>/dev/null || true

# 复制重要目录
echo -e "${YELLOW}[3/6] 复制重要目录...${NC}"

# source_code目录（所有Python API文件）
if [ -d "source_code" ]; then
    echo "  ✓ 复制 source_code/ 目录"
    cp -r source_code "${BACKUP_PATH}/"
else
    echo "  ⚠ source_code/ 不存在"
fi

# panic_paged_v2目录
if [ -d "panic_paged_v2" ]; then
    echo "  ✓ 复制 panic_paged_v2/ 目录"
    cp -r panic_paged_v2 "${BACKUP_PATH}/"
else
    echo "  ⚠ panic_paged_v2/ 不存在"
fi

# panic_v3目录
if [ -d "panic_v3" ]; then
    echo "  ✓ 复制 panic_v3/ 目录"
    cp -r panic_v3 "${BACKUP_PATH}/"
else
    echo "  ⚠ panic_v3/ 不存在"
fi

# major-events-system目录
if [ -d "major-events-system" ]; then
    echo "  ✓ 复制 major-events-system/ 目录"
    cp -r major-events-system "${BACKUP_PATH}/"
else
    echo "  ⚠ major-events-system/ 不存在（可能未创建）"
fi

# templates目录
if [ -d "templates" ]; then
    echo "  ✓ 复制 templates/ 目录（HTML模板）"
    cp -r templates "${BACKUP_PATH}/"
fi

# static目录
if [ -d "static" ]; then
    echo "  ✓ 复制 static/ 目录（静态文件）"
    cp -r static "${BACKUP_PATH}/"
fi

# config目录
if [ -d "config" ]; then
    echo "  ✓ 复制 config/ 目录（配置文件）"
    cp -r config "${BACKUP_PATH}/"
fi

# pm2目录
if [ -d "pm2" ]; then
    echo "  ✓ 复制 pm2/ 目录（PM2配置）"
    cp -r pm2 "${BACKUP_PATH}/"
fi

# ecosystem.config.js
if [ -f "ecosystem.config.js" ]; then
    echo "  ✓ 复制 ecosystem.config.js（PM2生态配置）"
    cp ecosystem.config.js "${BACKUP_PATH}/"
fi

# monitors目录
if [ -d "monitors" ]; then
    echo "  ✓ 复制 monitors/ 目录（监控脚本）"
    cp -r monitors "${BACKUP_PATH}/"
fi

# scripts目录
if [ -d "scripts" ]; then
    echo "  ✓ 复制 scripts/ 目录（工具脚本）"
    cp -r scripts "${BACKUP_PATH}/"
fi

# price_position_v2目录
if [ -d "price_position_v2" ]; then
    echo "  ✓ 复制 price_position_v2/ 目录"
    cp -r price_position_v2 "${BACKUP_PATH}/"
fi

# code目录
if [ -d "code" ]; then
    echo "  ✓ 复制 code/ 目录"
    cp -r code "${BACKUP_PATH}/"
fi

# tests目录
if [ -d "tests" ]; then
    echo "  ✓ 复制 tests/ 目录（测试文件）"
    cp -r tests "${BACKUP_PATH}/"
fi

# 复制所有数据文件
echo -e "${YELLOW}[4/6] 复制数据文件（全部数据，非7天）...${NC}"
if [ -d "data" ]; then
    echo "  ✓ 复制 data/ 目录（所有JSONL数据文件）"
    echo "    这可能需要较长时间..."
    cp -r data "${BACKUP_PATH}/"
    
    # 统计数据大小
    DATA_SIZE=$(du -sh "${BACKUP_PATH}/data" | cut -f1)
    echo "    数据目录大小: ${DATA_SIZE}"
else
    echo "  ⚠ data/ 不存在"
fi

# 复制文档
echo -e "${YELLOW}[5/6] 复制文档文件...${NC}"
if [ -d "docs" ]; then
    echo "  ✓ 复制 docs/ 目录（所有文档）"
    cp -r docs "${BACKUP_PATH}/"
fi

# 复制所有根目录的Markdown文件
echo "  ✓ 复制根目录Markdown文档"
find . -maxdepth 1 -name "*.md" -exec cp {} "${BACKUP_PATH}/" \;

# 复制requirements.txt
if [ -f "requirements.txt" ]; then
    echo "  ✓ 复制 requirements.txt（Python依赖）"
    cp requirements.txt "${BACKUP_PATH}/"
fi

# 复制package.json（如果存在）
if [ -f "package.json" ]; then
    echo "  ✓ 复制 package.json（Node.js依赖）"
    cp package.json "${BACKUP_PATH}/"
fi

# 创建部署信息文件
echo -e "${YELLOW}[6/6] 创建部署信息文件...${NC}"
cat > "${BACKUP_PATH}/DEPLOYMENT_INFO.txt" << EOF
============================================================
完整项目备份信息
============================================================

备份时间: ${TIMESTAMP}
源目录: ${PROJECT_DIR}
备份目录: ${BACKUP_PATH}

============================================================
系统环境信息
============================================================

操作系统: $(uname -s)
内核版本: $(uname -r)
Python版本: $(python3 --version 2>&1)
Node.js版本: $(node --version 2>&1 || echo "未安装")
PM2版本: $(pm2 --version 2>&1 || echo "未安装")

============================================================
目录结构
============================================================

$(tree -L 2 -d "${BACKUP_PATH}" 2>/dev/null || find "${BACKUP_PATH}" -type d -maxdepth 2)

============================================================
文件统计
============================================================

Python文件数: $(find "${BACKUP_PATH}" -name "*.py" | wc -l)
HTML文件数: $(find "${BACKUP_PATH}" -name "*.html" | wc -l)
Markdown文档数: $(find "${BACKUP_PATH}" -name "*.md" | wc -l)
JSON配置文件数: $(find "${BACKUP_PATH}" -name "*.json" | wc -l)
Shell脚本数: $(find "${BACKUP_PATH}" -name "*.sh" | wc -l)

============================================================
数据文件统计
============================================================

data目录大小: $(du -sh "${BACKUP_PATH}/data" 2>/dev/null | cut -f1 || echo "N/A")
JSONL文件数: $(find "${BACKUP_PATH}/data" -name "*.jsonl" 2>/dev/null | wc -l || echo "0")

============================================================
PM2进程状态（备份时）
============================================================

$(pm2 list 2>&1 || echo "PM2未运行")

============================================================
pip依赖列表
============================================================

$(pip3 list 2>&1 || echo "无法获取pip列表")

EOF

echo "  ✓ 部署信息已保存到 DEPLOYMENT_INFO.txt"

# 压缩备份
echo ""
echo -e "${YELLOW}正在压缩备份文件...${NC}"
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"

# 计算大小和MD5
BACKUP_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
BACKUP_MD5=$(md5sum "${BACKUP_NAME}.tar.gz" | cut -d' ' -f1)

# 清理临时目录
rm -rf "${BACKUP_NAME}"

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}   ✅ 备份完成！${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${GREEN}📦 备份文件信息：${NC}"
echo -e "  文件名: ${BACKUP_NAME}.tar.gz"
echo -e "  位置: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo -e "  大小: ${BACKUP_SIZE}"
echo -e "  MD5: ${BACKUP_MD5}"
echo ""
echo -e "${BLUE}📋 恢复命令：${NC}"
echo -e "  cd ${BACKUP_DIR}"
echo -e "  tar -xzf ${BACKUP_NAME}.tar.gz"
echo -e "  cd ${BACKUP_NAME}"
echo -e "  # 查看 DEPLOYMENT_GUIDE.md 获取详细部署说明"
echo ""
echo -e "${YELLOW}⚠️  注意事项：${NC}"
echo -e "  1. 此备份包含所有数据文件（非7天）"
echo -e "  2. 不包含 logs/、node_modules/、backups/、__pycache__/"
echo -e "  3. 请妥善保管备份文件"
echo -e "  4. 恢复前请先阅读 DEPLOYMENT_GUIDE.md"
echo ""
