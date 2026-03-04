#!/bin/bash
#
# 备份验证和快速恢复测试脚本
# 用于验证备份文件的完整性
#
# 使用方法: bash verify_backup.sh <backup_file.tar.gz>
#

if [ $# -eq 0 ]; then
    echo "❌ 错误：请提供备份文件路径"
    echo "使用方法: bash verify_backup.sh <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 错误：备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "============================================================"
echo "🔍 开始验证备份文件"
echo "============================================================"
echo "📦 备份文件: $BACKUP_FILE"
echo "💾 文件大小: $(du -sh $BACKUP_FILE | awk '{print $1}')"
echo "============================================================"
echo ""

# 1. 测试压缩文件完整性
echo "📝 [1/7] 测试压缩文件完整性..."
if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    echo "   ✅ 压缩文件完整"
    TOTAL_FILES=$(tar -tzf "$BACKUP_FILE" | wc -l)
    echo "   📊 包含文件数: $TOTAL_FILES"
else
    echo "   ❌ 压缩文件损坏！"
    exit 1
fi

# 2. 检查核心目录
echo ""
echo "📁 [2/7] 检查核心目录..."
REQUIRED_DIRS=(
    "python_core"
    "source_code"
    "code"
    "config"
    "monitors"
    "templates"
    "data"
    "config_files"
    "system_info"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if tar -tzf "$BACKUP_FILE" | grep -q "^[^/]*/${dir}/"; then
        echo "   ✅ ${dir}/"
    else
        echo "   ⚠️  ${dir}/ 缺失"
    fi
done

# 3. 检查关键文件
echo ""
echo "📄 [3/7] 检查关键文件..."
REQUIRED_FILES=(
    "python_core/app.py"
    "config_files/requirements.txt"
    "config_files/.env"
    "config_files/ecosystem.config.js"
    "config_files/pm2_processes.json"
    "system_info/pip_freeze.txt"
    "DEPLOYMENT_GUIDE.md"
    "BACKUP_MANIFEST.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if tar -tzf "$BACKUP_FILE" | grep -q "/${file}\$"; then
        echo "   ✅ ${file}"
    else
        echo "   ⚠️  ${file} 缺失"
    fi
done

# 4. 检查 Python 文件数量
echo ""
echo "🐍 [4/7] 检查 Python 文件..."
PY_COUNT=$(tar -tzf "$BACKUP_FILE" | grep -c "\.py$")
echo "   📊 Python 文件数: $PY_COUNT"
if [ $PY_COUNT -ge 80 ]; then
    echo "   ✅ Python 文件数量正常（预期 ≥80）"
else
    echo "   ⚠️  Python 文件数量偏少（预期 ≥80，实际 $PY_COUNT）"
fi

# 5. 检查数据文件
echo ""
echo "💾 [5/7] 检查数据文件..."
JSONL_COUNT=$(tar -tzf "$BACKUP_FILE" | grep -c "\.jsonl$")
echo "   📊 JSONL 数据文件数: $JSONL_COUNT"
if [ $JSONL_COUNT -ge 1000 ]; then
    echo "   ✅ 数据文件数量正常（预期 ≥1000）"
else
    echo "   ⚠️  数据文件数量偏少（预期 ≥1000，实际 $JSONL_COUNT）"
fi

# 6. 检查模板文件
echo ""
echo "📋 [6/7] 检查模板文件..."
HTML_COUNT=$(tar -tzf "$BACKUP_FILE" | grep -c "\.html$")
echo "   📊 HTML 模板数: $HTML_COUNT"
if [ $HTML_COUNT -ge 50 ]; then
    echo "   ✅ 模板文件数量正常（预期 ≥50）"
else
    echo "   ⚠️  模板文件数量偏少（预期 ≥50，实际 $HTML_COUNT）"
fi

# 7. 提取并显示备份清单
echo ""
echo "📋 [7/7] 提取备份清单..."
TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR" "*/BACKUP_MANIFEST.txt" 2>/dev/null

if [ -f "$TEMP_DIR"/*/BACKUP_MANIFEST.txt ]; then
    echo ""
    echo "============================================================"
    echo "📊 备份清单"
    echo "============================================================"
    cat "$TEMP_DIR"/*/BACKUP_MANIFEST.txt
    rm -rf "$TEMP_DIR"
else
    echo "   ⚠️  无法提取备份清单"
fi

# 总结
echo ""
echo "============================================================"
echo "✅ 验证完成"
echo "============================================================"
echo "📦 备份文件: $BACKUP_FILE"
echo "📊 统计信息:"
echo "   - 总文件数: $TOTAL_FILES"
echo "   - Python 文件: $PY_COUNT"
echo "   - JSONL 数据: $JSONL_COUNT"
echo "   - HTML 模板: $HTML_COUNT"
echo ""
echo "🚀 恢复提示:"
echo "   1. 解压: tar -xzf $BACKUP_FILE"
echo "   2. 查看: cat */DEPLOYMENT_GUIDE.md"
echo "   3. 部署: 按照部署指南操作"
echo "============================================================"
