/**
 * PM2 Ecosystem Configuration - Production Deployment
 * 完整系统部署配置
 */

module.exports = {
  apps: [
    // Flask Web Application - 主应用
    {
      name: 'flask-app',
      script: 'app.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        FLASK_ENV: 'production',
        PORT: 5000,
        PYTHONPATH: '/home/user/webapp:/home/user/webapp/source_code'
      },
      error_file: '/home/user/webapp/logs/flask-app-error.log',
      out_file: '/home/user/webapp/logs/flask-app-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    
    // Core Data Collectors
    {
      name: 'signal-collector',
      script: 'source_code/signal_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/signal-collector-error.log',
      out_file: '/home/user/webapp/logs/signal-collector-out.log'
    },
    {
      name: 'liquidation-1h-collector',
      script: 'source_code/liquidation_1h_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/liquidation-1h-error.log',
      out_file: '/home/user/webapp/logs/liquidation-1h-out.log'
    },
    {
      name: 'crypto-index-collector',
      script: 'source_code/crypto_index_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/crypto-index-error.log',
      out_file: '/home/user/webapp/logs/crypto-index-out.log'
    },
    {
      name: 'v1v2-collector',
      script: 'source_code/v1v2_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/v1v2-collector-error.log',
      out_file: '/home/user/webapp/logs/v1v2-collector-out.log'
    },
    {
      name: 'price-speed-collector',
      script: 'source_code/price_speed_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/price-speed-error.log',
      out_file: '/home/user/webapp/logs/price-speed-out.log'
    },
    {
      name: 'sar-slope-collector',
      script: 'source_code/sar_slope_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/sar-slope-error.log',
      out_file: '/home/user/webapp/logs/sar-slope-out.log'
    },
    {
      name: 'price-comparison-collector',
      script: 'source_code/price_comparison_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/price-comparison-error.log',
      out_file: '/home/user/webapp/logs/price-comparison-out.log'
    },
    {
      name: 'financial-indicators-collector',
      script: 'source_code/financial_indicators_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/financial-indicators-error.log',
      out_file: '/home/user/webapp/logs/financial-indicators-out.log'
    },
    {
      name: 'okx-day-change-collector',
      script: 'source_code/okx_day_change_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/okx-day-change-error.log',
      out_file: '/home/user/webapp/logs/okx-day-change-out.log'
    },
    {
      name: 'price-baseline-collector',
      script: 'source_code/price_baseline_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/price-baseline-error.log',
      out_file: '/home/user/webapp/logs/price-baseline-out.log'
    },
    {
      name: 'sar-bias-stats-collector',
      script: 'source_code/sar_bias_stats_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/sar-bias-stats-error.log',
      out_file: '/home/user/webapp/logs/sar-bias-stats-out.log'
    },
    {
      name: 'panic-wash-collector',
      script: 'source_code/panic_wash_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/panic-wash-error.log',
      out_file: '/home/user/webapp/logs/panic-wash-out.log'
    },
    {
      name: 'coin-change-tracker',
      script: 'source_code/coin_change_tracker.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/coin-change-tracker-error.log',
      out_file: '/home/user/webapp/logs/coin-change-tracker-out.log'
    },
    
    // Monitoring & Management
    {
      name: 'data-health-monitor',
      script: 'source_code/data_health_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      error_file: '/home/user/webapp/logs/data-health-error.log',
      out_file: '/home/user/webapp/logs/data-health-out.log'
    },
    {
      name: 'system-health-monitor',
      script: 'source_code/system_health_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      error_file: '/home/user/webapp/logs/system-health-error.log',
      out_file: '/home/user/webapp/logs/system-health-out.log'
    },
    {
      name: 'liquidation-alert-monitor',
      script: 'code/python/liquidation_alert_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      max_memory_restart: '300M',
      error_file: '/home/user/webapp/logs/liquidation-alert-error.log',
      out_file: '/home/user/webapp/logs/liquidation-alert-out.log'
    },
    
    // JSONL Managers
    {
      name: 'dashboard-jsonl-manager',
      script: 'source_code/dashboard_jsonl_manager.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/dashboard-jsonl-error.log',
      out_file: '/home/user/webapp/logs/dashboard-jsonl-out.log'
    },
    {
      name: 'gdrive-jsonl-manager',
      script: 'source_code/gdrive_jsonl_manager.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/gdrive-jsonl-error.log',
      out_file: '/home/user/webapp/logs/gdrive-jsonl-out.log'
    },
    
    // OKX Trading Systems
    {
      name: 'okx-tpsl-monitor',
      script: 'source_code/okx_tpsl_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/okx-tpsl-monitor-error.log',
      out_file: '/home/user/webapp/logs/okx-tpsl-monitor-out.log'
    },
    {
      name: 'okx-trade-history',
      script: 'source_code/okx_trade_history_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/okx-trade-history-error.log',
      out_file: '/home/user/webapp/logs/okx-trade-history-out.log'
    },
    
    // Market Analysis Systems
    {
      name: 'market-sentiment-collector',
      script: 'source_code/market_sentiment_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/market-sentiment-error.log',
      out_file: '/home/user/webapp/logs/market-sentiment-out.log'
    },
    {
      name: 'price-position-collector',
      script: 'source_code/price_position_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/price-position-error.log',
      out_file: '/home/user/webapp/logs/price-position-out.log'
    },
    {
      name: 'rsi-takeprofit-monitor',
      script: 'source_code/rsi_takeprofit_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/rsi-takeprofit-error.log',
      out_file: '/home/user/webapp/logs/rsi-takeprofit-out.log'
    },
    
    // Bottom Signal Long Monitor - 见底信号做多监控
    {
      name: 'bottom-signal-long-monitor',
      script: 'source_code/bottom_signal_long_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/home/user/webapp/logs/bottom-signal-long-error.log',
      out_file: '/home/user/webapp/logs/bottom-signal-long-out.log'
    },
    
    // Coin Change Prediction Monitor - 币种涨跌预判监控
    {
      name: 'coin-change-predictor',
      script: 'monitors/coin_change_prediction_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONPATH: '/home/user/webapp'
      },
      error_file: '/home/user/webapp/logs/coin-change-predictor-error.log',
      out_file: '/home/user/webapp/logs/coin-change-predictor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
