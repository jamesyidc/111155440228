/**
 * PM2 Ecosystem Configuration - Updated for Available Scripts
 * 自动部署配置 - 基于实际可用的脚本
 * 
 * 使用方法:
 *   pm2 start ecosystem.config.js
 *   pm2 save
 */

module.exports = {
  apps: [
    // Flask Web Application
    {
      name: 'flask-app',
      script: 'app.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        FLASK_ENV: 'production',
        PORT: 5000
      }
    },
    
    // Core Data Collectors - Actually Available
    {
      name: 'signal-collector',
      script: 'source_code/signal_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'liquidation-1h-collector',
      script: 'source_code/liquidation_1h_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'crypto-index-collector',
      script: 'source_code/crypto_index_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'v1v2-collector',
      script: 'source_code/v1v2_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'price-speed-collector',
      script: 'source_code/price_speed_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'sar-collector',
      script: 'source_code/sar_collector_fixed.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'sar-slope-updater',
      script: 'source_code/update_latest_sar_slope.py',
      args: '--daemon --interval 300',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'sar-slope-collector',
      script: 'source_code/sar_slope_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'price-comparison-collector',
      script: 'source_code/price_comparison_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'financial-indicators-collector',
      script: 'source_code/financial_indicators_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'okx-day-change-collector',
      script: 'source_code/okx_day_change_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'price-baseline-collector',
      script: 'source_code/price_baseline_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'sar-bias-stats-collector',
      script: 'source_code/sar_bias_stats_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'panic-wash-collector',
      script: 'source_code/panic_wash_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'coin-change-tracker',
      script: 'source_code/coin_change_tracker_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'okx-trade-history-collector',
      script: 'source_code/okx_trade_history_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'okx-trading-marks-collector',
      script: 'source_code/okx_trading_marks_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'price-position-collector',
      script: 'source_code/price_position_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    
    // Monitoring & Management
    {
      name: 'data-health-monitor',
      script: 'source_code/data_health_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'system-health-monitor',
      script: 'source_code/system_health_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'major-events-monitor',
      script: 'major-events-system/major_events_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'liquidation-alert-monitor',
      script: 'liquidation_alert_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    // JSONL Managers
    {
      name: 'dashboard-jsonl-manager',
      script: 'source_code/dashboard_jsonl_manager.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    },
    {
      name: 'gdrive-jsonl-manager',
      script: 'source_code/gdrive_jsonl_manager.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true
    }
  ]
};
