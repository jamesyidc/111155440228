#!/bin/bash
# 自动恢复脚本
# 用于快速恢复项目到新环境

set -e

echo "=========================================="
echo "🔄 项目自动恢复脚本"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  请不要使用root用户运行此脚本"
   echo "   建议使用: sudo -u user bash restore_project.sh"
   exit 1
fi

# 定义变量
BACKUP_DIR=$(pwd)
TARGET_DIR="/home/user/webapp"
CURRENT_USER=$(whoami)

echo "📋 恢复配置:"
echo "  - 当前用户: ${CURRENT_USER}"
echo "  - 备份目录: ${BACKUP_DIR}"
echo "  - 目标目录: ${TARGET_DIR}"
echo ""

# 1. 检查系统依赖
echo "============================================"
echo "🔍 1. 检查系统依赖"
echo "============================================"

check_command() {
    if command -v $1 &> /dev/null; then
        echo "  ✅ $1 已安装"
        $1 --version 2>&1 | head -1
    else
        echo "  ❌ $1 未安装"
        echo "     请先安装: sudo apt install $2"
        return 1
    fi
}

check_command "python3" "python3"
check_command "pip" "python3-pip" || check_command "pip3" "python3-pip"
check_command "node" "nodejs"
check_command "npm" "npm"
check_command "pm2" "npm install -g pm2" || echo "  💡 安装PM2: sudo npm install -g pm2"

echo ""

# 2. 创建目标目录
echo "============================================"
echo "📁 2. 准备目标目录"
echo "============================================"

if [ -d "${TARGET_DIR}" ]; then
    echo "  ⚠️  目标目录已存在: ${TARGET_DIR}"
    read -p "  是否备份现有目录? (y/n): " BACKUP_EXISTING
    
    if [ "$BACKUP_EXISTING" = "y" ]; then
        BACKUP_OLD="${TARGET_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
        echo "  📦 备份到: ${BACKUP_OLD}"
        sudo mv "${TARGET_DIR}" "${BACKUP_OLD}"
    else
        echo "  ⚠️  将覆盖现有文件"
    fi
fi

echo "  ✓ 创建目标目录: ${TARGET_DIR}"
sudo mkdir -p "${TARGET_DIR}"
sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "${TARGET_DIR}"

echo ""

# 3. 复制文件
echo "============================================"
echo "📦 3. 复制项目文件"
echo "============================================"

echo "  🔄 正在复制文件..."
cp -rv "${BACKUP_DIR}"/* "${TARGET_DIR}/" 2>&1 | grep -v "omitting directory" | head -20
echo "  ... (更多文件)"
echo ""
echo "  ✅ 文件复制完成"

# 设置权限
sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "${TARGET_DIR}"
chmod -R 755 "${TARGET_DIR}"

echo ""

# 4. 安装Python依赖
echo "============================================"
echo "🐍 4. 安装Python依赖"
echo "============================================"

cd "${TARGET_DIR}"

if [ -f "requirements.txt" ]; then
    echo "  📋 发现requirements.txt"
    read -p "  是否创建虚拟环境? (推荐) (y/n): " USE_VENV
    
    if [ "$USE_VENV" = "y" ]; then
        echo "  🔧 创建虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
        echo "  ✅ 虚拟环境已激活"
    fi
    
    echo "  📥 安装Python依赖..."
    pip install -r requirements.txt
    echo "  ✅ Python依赖安装完成"
else
    echo "  ⚠️  未找到requirements.txt"
    echo "  💡 手动安装依赖: pip install flask requests pandas"
fi

echo ""

# 5. 配置文件检查
echo "============================================"
echo "⚙️  5. 检查配置文件"
echo "============================================"

# Telegram配置
TG_CONFIG="${TARGET_DIR}/config/configs/telegram_config.json"
if [ -f "${TG_CONFIG}" ]; then
    echo "  ✅ Telegram配置文件存在"
    
    # 检查是否包含占位符
    if grep -q "YOUR_BOT_TOKEN" "${TG_CONFIG}"; then
        echo "  ⚠️  Telegram配置包含占位符，需要更新"
        echo "  💡 编辑: nano ${TG_CONFIG}"
    else
        echo "  ✓ Telegram配置看起来正常"
    fi
else
    echo "  ❌ Telegram配置文件不存在"
    echo "  💡 创建: ${TG_CONFIG}"
fi

# OKX配置
OKX_CONFIG="${TARGET_DIR}/config/configs/okx_config.json"
if [ -f "${OKX_CONFIG}" ]; then
    echo "  ✅ OKX配置文件存在"
else
    echo "  ⚠️  OKX配置文件不存在（如果不使用OKX可忽略）"
fi

echo ""

# 6. 数据目录检查
echo "============================================"
echo "💾 6. 检查数据目录"
echo "============================================"

DATA_DIR="${TARGET_DIR}/data"
if [ -d "${DATA_DIR}" ]; then
    DATA_SIZE=$(du -sh "${DATA_DIR}" | awk '{print $1}')
    FILE_COUNT=$(find "${DATA_DIR}" -type f | wc -l)
    
    echo "  ✅ 数据目录存在"
    echo "  📊 数据大小: ${DATA_SIZE}"
    echo "  📁 文件数量: ${FILE_COUNT}"
    
    # 检查最新数据
    echo ""
    echo "  📅 最新数据文件:"
    find "${DATA_DIR}" -type f -name "*.jsonl" -o -name "*.json" | sort | tail -5
else
    echo "  ❌ 数据目录不存在"
    echo "  💡 创建: mkdir -p ${DATA_DIR}"
fi

echo ""

# 7. PM2配置
echo "============================================"
echo "🔧 7. 配置PM2"
echo "============================================"

if command -v pm2 &> /dev/null; then
    echo "  ✅ PM2已安装"
    
    # 检查ecosystem.config.js
    if [ -f "${TARGET_DIR}/ecosystem.config.js" ]; then
        echo "  ✅ ecosystem.config.js存在"
        echo ""
        read -p "  是否立即启动PM2服务? (y/n): " START_PM2
        
        if [ "$START_PM2" = "y" ]; then
            cd "${TARGET_DIR}"
            pm2 start ecosystem.config.js
            pm2 save
            echo "  ✅ PM2服务已启动"
            echo ""
            pm2 list
        else
            echo "  💡 稍后启动: cd ${TARGET_DIR} && pm2 start ecosystem.config.js"
        fi
    else
        echo "  ⚠️  ecosystem.config.js不存在"
        echo "  💡 手动启动: pm2 start app.py --name flask-app --interpreter python3"
    fi
    
    # PM2开机自启
    echo ""
    read -p "  是否设置PM2开机自启? (y/n): " PM2_STARTUP
    if [ "$PM2_STARTUP" = "y" ]; then
        pm2 startup
        echo ""
        echo "  💡 请执行上面显示的sudo命令来完成设置"
    fi
else
    echo "  ❌ PM2未安装"
    echo "  💡 安装: sudo npm install -g pm2"
fi

echo ""

# 8. 测试Flask应用
echo "============================================"
echo "🧪 8. 测试Flask应用"
echo "============================================"

if [ -f "${TARGET_DIR}/app.py" ]; then
    echo "  ✅ app.py存在"
    
    # 检查端口
    if netstat -tlnp 2>/dev/null | grep -q ":9002"; then
        echo "  ✅ 端口9002已在监听"
        echo ""
        echo "  🌐 测试API..."
        curl -s http://localhost:9002/ | head -5 || echo "  ⚠️  API未响应"
    else
        echo "  ⚠️  端口9002未监听"
        echo "  💡 启动Flask: python3 ${TARGET_DIR}/app.py"
    fi
else
    echo "  ❌ app.py不存在"
fi

echo ""

# 9. 完成总结
echo "============================================"
echo "✅ 恢复完成！"
echo "============================================"
echo ""
echo "📋 后续步骤："
echo ""
echo "1. 检查配置文件:"
echo "   nano ${TARGET_DIR}/config/configs/telegram_config.json"
echo ""
echo "2. 启动服务（如果还未启动）:"
echo "   cd ${TARGET_DIR}"
echo "   pm2 start ecosystem.config.js"
echo "   pm2 save"
echo ""
echo "3. 查看服务状态:"
echo "   pm2 list"
echo "   pm2 logs flask-app --lines 50"
echo ""
echo "4. 访问Web界面:"
echo "   http://localhost:9002/"
echo ""
echo "5. 查看详细文档:"
echo "   cat ${TARGET_DIR}/DEPLOYMENT_GUIDE.md"
echo ""
echo "============================================"
echo "📞 如有问题，请查看:"
echo "   - 部署指南: ${TARGET_DIR}/DEPLOYMENT_GUIDE.md"
echo "   - 备份信息: ${TARGET_DIR}/BACKUP_INFO.txt"
echo "   - 系统信息: ${TARGET_DIR}/system_info/"
echo "============================================"
