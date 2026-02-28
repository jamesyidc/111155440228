#!/bin/bash
# 27币追踪系统数据迁移自动化脚本
# 用法: bash migrate_coin_tracker.sh [export|import]

set -e  # 遇到错误立即退出

WEBAPP_DIR="/home/user/webapp"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="coin_tracker_backup_${BACKUP_DATE}.json"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 导出函数
do_export() {
    log_step "=========================================="
    log_step "  27币追踪系统 - 数据导出流程"
    log_step "=========================================="
    echo ""
    
    cd "$WEBAPP_DIR"
    
    # 1. 停止采集器
    log_step "步骤1: 停止数据采集器"
    if pm2 list | grep -q "coin-change-tracker.*online"; then
        pm2 stop coin-change-tracker
        log_info "✓ 采集器已停止"
    else
        log_warn "采集器未运行，跳过"
    fi
    sleep 2
    
    # 2. 检查数据完整性
    log_step "步骤2: 检查数据完整性"
    JSONL_COUNT=$(ls -1 data/coin_change_tracker/*.jsonl 2>/dev/null | wc -l)
    DATA_SIZE=$(du -sh data/coin_change_tracker/ | cut -f1)
    log_info "  JSONL文件数: $JSONL_COUNT"
    log_info "  数据目录大小: $DATA_SIZE"
    
    if [ "$JSONL_COUNT" -eq 0 ]; then
        log_error "未找到任何JSONL文件，导出终止"
        exit 1
    fi
    
    # 3. 导出数据
    log_step "步骤3: 使用数据同步工具导出"
    if [ -f "scripts/export_daily_data.js" ]; then
        node scripts/export_daily_data.js http://localhost:9002 "$BACKUP_FILE"
    else
        log_warn "数据同步工具不可用，使用手动打包"
        tar -czf "${BACKUP_FILE%.json}.tar.gz" \
            data/coin_change_tracker/*.jsonl \
            data/coin_change_tracker/baseline_*.json \
            data/crash_warning_events/ 2>/dev/null || true
        BACKUP_FILE="${BACKUP_FILE%.json}.tar.gz"
    fi
    
    # 4. 验证导出
    log_step "步骤4: 验证导出结果"
    if [ -f "$BACKUP_FILE" ]; then
        FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log_info "✓ 导出完成!"
        echo ""
        echo "  📦 备份文件: $BACKUP_FILE"
        echo "  📊 文件大小: $FILE_SIZE"
        
        if [[ "$BACKUP_FILE" == *.json ]]; then
            FILE_COUNT=$(jq '.files | length' "$BACKUP_FILE" 2>/dev/null || echo "N/A")
            echo "  📁 文件数量: $FILE_COUNT"
        fi
    else
        log_error "导出失败: 未找到备份文件"
        exit 1
    fi
    
    # 5. 重启采集器
    log_step "步骤5: 重启数据采集器"
    pm2 start coin-change-tracker
    log_info "✓ 采集器已重启"
    
    echo ""
    log_step "=========================================="
    log_info "✅ 导出流程完成!"
    log_step "=========================================="
    echo ""
    echo "下一步操作:"
    echo "  1. 下载备份文件: $BACKUP_FILE"
    echo "  2. 在新系统上执行: ./migrate_coin_tracker.sh import $BACKUP_FILE"
    echo ""
}

# 导入函数
do_import() {
    if [ -z "$2" ]; then
        log_error "请指定备份文件"
        echo "用法: $0 import <backup_file>"
        exit 1
    fi
    
    IMPORT_FILE="$2"
    
    if [ ! -f "$IMPORT_FILE" ]; then
        log_error "备份文件不存在: $IMPORT_FILE"
        exit 1
    fi
    
    log_step "=========================================="
    log_step "  27币追踪系统 - 数据导入流程"
    log_step "=========================================="
    echo ""
    
    cd "$WEBAPP_DIR"
    
    # 1. 创建必要目录
    log_step "步骤1: 创建数据目录"
    mkdir -p data/coin_change_tracker
    mkdir -p data/crash_warning_events
    mkdir -p backups
    log_info "✓ 目录已创建"
    
    # 2. 备份现有数据
    log_step "步骤2: 备份现有数据"
    if [ -d "data/coin_change_tracker" ] && [ "$(ls -A data/coin_change_tracker 2>/dev/null)" ]; then
        EXISTING_BACKUP="backups/existing_data_${BACKUP_DATE}.tar.gz"
        tar -czf "$EXISTING_BACKUP" data/coin_change_tracker/ data/crash_warning_events/ 2>/dev/null || true
        BACKUP_SIZE=$(du -h "$EXISTING_BACKUP" | cut -f1)
        log_warn "现有数据已备份至: $EXISTING_BACKUP ($BACKUP_SIZE)"
    else
        log_info "无现有数据，跳过备份"
    fi
    
    # 3. 导入数据
    log_step "步骤3: 导入数据"
    if [[ "$IMPORT_FILE" == *.json ]]; then
        log_info "使用数据同步工具导入..."
        if [ -f "scripts/import_daily_data.js" ]; then
            node scripts/import_daily_data.js http://localhost:9002 "$IMPORT_FILE"
        else
            log_error "数据同步工具不可用"
            exit 1
        fi
    elif [[ "$IMPORT_FILE" == *.tar.gz ]]; then
        log_info "解压tar.gz备份文件..."
        tar -xzf "$IMPORT_FILE" -C "$WEBAPP_DIR"
    else
        log_error "不支持的文件格式: $IMPORT_FILE"
        exit 1
    fi
    
    # 4. 验证导入
    log_step "步骤4: 验证导入结果"
    JSONL_COUNT=$(ls -1 data/coin_change_tracker/*.jsonl 2>/dev/null | wc -l)
    BASELINE_COUNT=$(ls -1 data/coin_change_tracker/baseline_*.json 2>/dev/null | wc -l)
    DATA_SIZE=$(du -sh data/coin_change_tracker/ | cut -f1)
    
    log_info "✓ 导入完成!"
    echo ""
    echo "  📊 JSONL文件: $JSONL_COUNT 个"
    echo "  📊 基线文件: $BASELINE_COUNT 个"
    echo "  📊 数据大小: $DATA_SIZE"
    echo ""
    
    if [ "$JSONL_COUNT" -eq 0 ]; then
        log_error "导入失败: 未找到JSONL文件"
        exit 1
    fi
    
    # 5. 设置权限
    log_step "步骤5: 设置文件权限"
    chmod 644 data/coin_change_tracker/* 2>/dev/null || true
    chmod 755 data/coin_change_tracker data/crash_warning_events
    log_info "✓ 权限已设置"
    
    # 6. 启动服务
    log_step "步骤6: 启动币种追踪采集器"
    pm2 delete coin-change-tracker 2>/dev/null || true
    pm2 start source_code/coin_change_tracker_collector.py \
        --name coin-change-tracker \
        --interpreter python3 \
        --cron-restart="0 2 * * *" \
        --log-date-format="YYYY-MM-DD HH:mm:ss"
    
    sleep 3
    log_info "✓ 采集器已启动"
    
    # 7. 重启Web服务
    log_step "步骤7: 重启Flask应用"
    pm2 restart flask-app
    sleep 2
    log_info "✓ Flask应用已重启"
    
    # 8. 健康检查
    log_step "步骤8: 健康检查"
    echo ""
    pm2 list | grep -E "coin-change-tracker|flask-app"
    echo ""
    
    # 9. 检查最新数据
    log_step "步骤9: 检查最新数据"
    LATEST_FILE=$(ls -t data/coin_change_tracker/coin_change_*.jsonl 2>/dev/null | head -1)
    if [ -n "$LATEST_FILE" ]; then
        LATEST_DATE=$(basename "$LATEST_FILE" | grep -oP '\d{8}')
        LINE_COUNT=$(wc -l < "$LATEST_FILE")
        log_info "  最新数据: $LATEST_DATE ($LINE_COUNT 条记录)"
    fi
    
    echo ""
    log_step "=========================================="
    log_info "✅ 导入流程完成!"
    log_step "=========================================="
    echo ""
    echo "系统已就绪! 请访问:"
    echo "  🌐 https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker"
    echo ""
    echo "验证检查:"
    echo "  ✓ 27个币种涨跌数据实时更新"
    echo "  ✓ RSI之和曲线显示正常 (灰色粗线)"
    echo "  ✓ 波峰标记正确 (B点绿色, A点橙色, C点灰色)"
    echo "  ✓ 暴跌预警卡片功能正常"
    echo ""
    echo "监控命令:"
    echo "  查看实时日志: pm2 logs coin-change-tracker --lines 0"
    echo "  查看服务状态: pm2 list"
    echo "  查看最新数据: tail -f data/coin_change_tracker/coin_change_\$(date +%Y%m%d).jsonl"
    echo ""
}

# 帮助信息
show_help() {
    cat << EOF
27币追踪系统数据迁移工具 v1.0

用法:
  $0 export                    导出当前系统数据
  $0 import <backup_file>       导入备份数据
  $0 help                      显示此帮助信息

示例:
  # 在旧系统上导出数据
  $0 export
  
  # 在新系统上导入数据
  $0 import coin_tracker_backup_20260224_133000.json
  
  # 或导入tar.gz备份
  $0 import coin_tracker_backup_20260224_133000.tar.gz

支持的备份格式:
  - JSON (数据同步工具生成)
  - tar.gz (手动打包生成)

相关文档:
  - DEPLOYMENT_DATA_MIGRATION_GUIDE.md  完整迁移指南
  - DATA_SYNC_GUIDE.md                  数据同步系统文档
  - DATA_SYNC_QUICK_REF.md              快速参考

系统信息:
  - 项目目录: $WEBAPP_DIR
  - 数据目录: $WEBAPP_DIR/data/coin_change_tracker
  - 系统URL: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai

技术支持:
  - GitHub: https://github.com/jamesyidc/1212335551
  - PR #1: https://github.com/jamesyidc/1212335551/pull/1

EOF
}

# 主逻辑
case "$1" in
    export)
        do_export
        ;;
    import)
        do_import "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "无效的命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
