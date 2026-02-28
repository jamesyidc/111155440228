#!/bin/bash
# 27币追踪系统 - 快速数据补齐脚本
# 用途: 重新部署后，一键补齐缺失的1-2小时数据

set -e

WEBAPP_DIR="/home/user/webapp"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 显示帮助
show_help() {
    cat << EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  27币追踪系统 - 数据补齐工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

用途: 重新部署后，补齐部署期间缺失的数据

用法:
  $0                     # 交互式补齐（询问时间范围）
  $0 --last-2h           # 补齐最近2小时（快速模式）
  $0 --last-1h           # 补齐最近1小时
  $0 --custom HH:MM HH:MM # 自定义时间范围
  $0 --help              # 显示帮助

示例:
  # 快速补齐最近2小时（推荐）
  $0 --last-2h
  
  # 补齐指定时间范围 (13:00 到 15:30)
  $0 --custom 13:00 15:30
  
  # 交互式输入时间
  $0

典型使用场景:
  1. 从旧系统备份数据: 14:00
  2. 传输+部署新系统: 14:00 - 15:30 (1.5小时)
  3. 启动新系统: 15:30
  4. 补齐缺失数据: ./quick_backfill.sh --last-2h

数据说明:
  - 补齐范围: 仅当天数据
  - 数据源: OKX历史K线API
  - 币种: 27个主流币种
  - 频率: 每分钟1条记录
  - 包含: 涨跌幅 + RSI指标

前提条件:
  ✓ 当天的基线文件已存在: baseline_YYYYMMDD.json
  ✓ Python3环境可用
  ✓ 必要的依赖包已安装: requests numpy pytz

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
}

# 检查环境
check_environment() {
    cd "$WEBAPP_DIR"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查依赖包
    python3 -c "import requests, numpy, pytz" 2>/dev/null || {
        log_error "Python依赖包缺失"
        echo ""
        echo "请安装依赖:"
        echo "  pip3 install requests numpy pytz"
        exit 1
    }
    
    # 检查数据目录
    if [ ! -d "data/coin_change_tracker" ]; then
        log_error "数据目录不存在: data/coin_change_tracker"
        exit 1
    fi
    
    # 检查基线文件
    TODAY=$(date +%Y%m%d)
    BASELINE_FILE="data/coin_change_tracker/baseline_${TODAY}.json"
    
    if [ ! -f "$BASELINE_FILE" ]; then
        log_error "基线文件不存在: $BASELINE_FILE"
        echo ""
        echo "解决方案:"
        echo "  1. 如果今天是新交易日，等待02:00自动生成"
        echo "  2. 或手动创建基线文件"
        echo "  3. 或使用昨天的数据目录"
        exit 1
    fi
}

# 快速补齐最近N小时
quick_backfill() {
    HOURS=$1
    
    log_step "快速补齐模式: 最近 ${HOURS} 小时"
    echo ""
    
    check_environment
    
    cd "$WEBAPP_DIR"
    
    # 计算时间范围
    NOW=$(date '+%Y-%m-%d %H:%M:%S')
    START_TIME=$(date -d "${HOURS} hours ago" '+%H:%M')
    END_TIME=$(date '+%H:%M')
    
    log_info "当前时间: $NOW"
    log_info "补齐范围: $START_TIME ~ $END_TIME"
    echo ""
    
    # 调用Python脚本
    python3 << EOF
import sys
sys.path.insert(0, '/home/user/webapp/scripts')

from backfill_today_data import backfill_data
from datetime import datetime, timedelta
import pytz

BEIJING_TZ = pytz.timezone('Asia/Shanghai')
now = datetime.now(BEIJING_TZ)

start_time = now - timedelta(hours=${HOURS})
start_time = start_time.replace(second=0, microsecond=0)
end_time = now.replace(second=0, microsecond=0)

backfill_data(start_time, end_time)
EOF
    
    if [ $? -eq 0 ]; then
        log_info "✅ 补齐完成!"
        echo ""
        log_info "下一步操作:"
        echo "  1. 查看实时日志: pm2 logs coin-change-tracker --lines 0"
        echo "  2. 访问Web界面: https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker"
    else
        log_error "补齐失败"
        exit 1
    fi
}

# 自定义时间范围补齐
custom_backfill() {
    START=$1
    END=$2
    
    log_step "自定义时间范围补齐"
    echo ""
    
    check_environment
    
    cd "$WEBAPP_DIR"
    
    NOW=$(date '+%Y-%m-%d %H:%M:%S')
    log_info "当前时间: $NOW"
    log_info "补齐范围: $START ~ $END"
    echo ""
    
    # 调用Python脚本
    python3 << EOF
import sys
sys.path.insert(0, '/home/user/webapp/scripts')

from backfill_today_data import backfill_data
from datetime import datetime
import pytz

BEIJING_TZ = pytz.timezone('Asia/Shanghai')
now = datetime.now(BEIJING_TZ)

try:
    start_hour, start_min = map(int, '${START}'.split(':'))
    end_hour, end_min = map(int, '${END}'.split(':'))
    
    start_time = now.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
    end_time = now.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
    
    backfill_data(start_time, end_time)
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_info "✅ 补齐完成!"
    else
        log_error "补齐失败"
        exit 1
    fi
}

# 交互式补齐
interactive_backfill() {
    log_step "交互式数据补齐"
    echo ""
    
    check_environment
    
    cd "$WEBAPP_DIR"
    
    # 调用Python脚本（交互式模式）
    python3 scripts/backfill_today_data.py
}

# 主逻辑
case "$1" in
    --last-2h)
        quick_backfill 2
        ;;
    --last-1h)
        quick_backfill 1
        ;;
    --custom)
        if [ -z "$2" ] || [ -z "$3" ]; then
            log_error "请指定时间范围"
            echo "用法: $0 --custom HH:MM HH:MM"
            echo "示例: $0 --custom 13:00 15:30"
            exit 1
        fi
        custom_backfill "$2" "$3"
        ;;
    --help|-h|help)
        show_help
        ;;
    "")
        interactive_backfill
        ;;
    *)
        log_error "无效的参数: $1"
        echo ""
        echo "用法: $0 [--last-2h | --last-1h | --custom HH:MM HH:MM | --help]"
        echo "或直接运行: $0 (交互式模式)"
        exit 1
        ;;
esac
