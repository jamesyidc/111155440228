#!/bin/bash
# 数据管理快捷命令脚本

case "$1" in
    scan)
        echo "🔍 正在扫描数据..."
        python3 source_code/data_manager.py
        ;;
    backup)
        echo "📦 正在创建完整备份..."
        python3 source_code/data_backup_service.py backup
        ;;
    backup-inc)
        echo "📥 正在创建增量备份..."
        python3 source_code/data_backup_service.py incremental
        ;;
    list)
        echo "📋 备份列表:"
        python3 source_code/data_backup_service.py list
        ;;
    restore)
        if [ -z "$2" ]; then
            echo "❌ 错误: 请指定备份名称"
            echo "用法: ./manage_data.sh restore <backup_name>"
            exit 1
        fi
        echo "🔄 正在恢复备份: $2"
        python3 source_code/data_backup_service.py restore "$2"
        ;;
    delete)
        if [ -z "$2" ]; then
            echo "❌ 错误: 请指定备份名称"
            echo "用法: ./manage_data.sh delete <backup_name>"
            exit 1
        fi
        echo "🗑️  正在删除备份: $2"
        python3 source_code/data_backup_service.py delete "$2"
        ;;
    stats)
        echo "📊 数据统计:"
        if [ -f "data/data_statistics.json" ]; then
            cat data/data_statistics.json | python3 -m json.tool | head -50
        else
            echo "⚠️  统计文件不存在，请先运行扫描: ./manage_data.sh scan"
        fi
        ;;
    *)
        echo "数据管理快捷命令"
        echo ""
        echo "用法: ./manage_data.sh <command> [参数]"
        echo ""
        echo "命令:"
        echo "  scan             扫描所有数据并生成统计报告"
        echo "  backup           创建完整备份（压缩）"
        echo "  backup-inc       创建增量备份"
        echo "  list             列出所有备份"
        echo "  restore <name>   恢复指定备份"
        echo "  delete <name>    删除指定备份"
        echo "  stats            查看数据统计摘要"
        echo ""
        echo "示例:"
        echo "  ./manage_data.sh scan"
        echo "  ./manage_data.sh backup"
        echo "  ./manage_data.sh list"
        echo "  ./manage_data.sh restore backup_20260216_150000"
        ;;
esac
