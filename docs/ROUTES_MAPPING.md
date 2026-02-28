# Flask 路由映射文档

> 📅 生成时间: 2026-02-07
> 📊 总路由数: 344
> 🗂️ 分类数: 76

## 目录

1. [🌐 Web Pages](#🌐-web-pages) - 83 路由
2. [🎯 Live Trading](#🎯-live-trading) - 2 路由
3. [🏠 Root/Homepage](#🏠-roothomepage) - 1 路由
4. [💰 Symbol Pages](#💰-symbol-pages) - 4 路由
5. [📈 K-Line Charts](#📈-k-line-charts) - 2 路由
6. [📊 SAR Slope System](#📊-sar-slope-system) - 4 路由
7. [📡 API - aligned-data](#📡-api---aligned-data) - 1 路由
8. [📡 API - anchor-profit](#📡-api---anchor-profit) - 6 路由
9. [📡 API - anchor-system](#📡-api---anchor-system) - 15 路由
10. [📡 API - backfill-monitor](#📡-api---backfill-monitor) - 2 路由
11. [📡 API - cache](#📡-api---cache) - 2 路由
12. [📡 API - chart](#📡-api---chart) - 1 路由
13. [📡 API - chart-config](#📡-api---chart-config) - 1 路由
14. [📡 API - coin-change-tracker](#📡-api---coin-change-tracker) - 4 路由
15. [📡 API - coin-price-tracker](#📡-api---coin-price-tracker) - 2 路由
16. [📡 API - coins](#📡-api---coins) - 1 路由
17. [📡 API - collectors](#📡-api---collectors) - 1 路由
18. [📡 API - count](#📡-api---count) - 1 路由
19. [📡 API - daily-tasks](#📡-api---daily-tasks) - 2 路由
20. [📡 API - data-health-monitor](#📡-api---data-health-monitor) - 4 路由
21. [📡 API - depth-chart-data](#📡-api---depth-chart-data) - 1 路由
22. [📡 API - depth-scores](#📡-api---depth-scores) - 1 路由
23. [📡 API - escape-signal-simple](#📡-api---escape-signal-simple) - 1 路由
24. [📡 API - escape-signal-stats](#📡-api---escape-signal-stats) - 7 路由
25. [📡 API - extreme-market-alerts](#📡-api---extreme-market-alerts) - 2 路由
26. [📡 API - extreme-tracking](#📡-api---extreme-tracking) - 3 路由
27. [📡 API - fear-greed](#📡-api---fear-greed) - 3 路由
28. [📡 API - folder-update-status](#📡-api---folder-update-status) - 1 路由
29. [📡 API - fund-monitor](#📡-api---fund-monitor) - 7 路由
30. [📡 API - gdrive-config](#📡-api---gdrive-config) - 4 路由
31. [📡 API - gdrive-detector](#📡-api---gdrive-detector) - 6 路由
32. [📡 API - gdrive-monitor](#📡-api---gdrive-monitor) - 1 路由
33. [📡 API - get-update-log](#📡-api---get-update-log) - 1 路由
34. [📡 API - health](#📡-api---health) - 1 路由
35. [📡 API - homepage](#📡-api---homepage) - 1 路由
36. [📡 API - index](#📡-api---index) - 5 路由
37. [📡 API - kline-indicators](#📡-api---kline-indicators) - 3 路由
38. [📡 API - kline-indicators-tv](#📡-api---kline-indicators-tv) - 2 路由
39. [📡 API - latest](#📡-api---latest) - 1 路由
40. [📡 API - liquidation](#📡-api---liquidation) - 1 路由
41. [📡 API - liquidation-1h](#📡-api---liquidation-1h) - 2 路由
42. [📡 API - list-recent-folders](#📡-api---list-recent-folders) - 1 路由
43. [📡 API - live-trading](#📡-api---live-trading) - 1 路由
44. [📡 API - major-events](#📡-api---major-events) - 5 路由
45. [📡 API - market-average-score](#📡-api---market-average-score) - 1 路由
46. [📡 API - modules](#📡-api---modules) - 1 路由
47. [📡 API - monitor](#📡-api---monitor) - 8 路由
48. [📡 API - okex-crypto-index](#📡-api---okex-crypto-index) - 1 路由
49. [📡 API - okx-accounts](#📡-api---okx-accounts) - 5 路由
50. [📡 API - okx-day-change](#📡-api---okx-day-change) - 2 路由
51. [📡 API - okx-trading](#📡-api---okx-trading) - 15 路由
52. [📡 API - opening-logic](#📡-api---opening-logic) - 1 路由
53. [📡 API - pair-protection](#📡-api---pair-protection) - 4 路由
54. [📡 API - panic](#📡-api---panic) - 4 路由
55. [📡 API - position](#📡-api---position) - 5 路由
56. [📡 API - price-comparison](#📡-api---price-comparison) - 5 路由
57. [📡 API - price-speed](#📡-api---price-speed) - 2 路由
58. [📡 API - query](#📡-api---query) - 3 路由
59. [📡 API - sar-slope](#📡-api---sar-slope) - 21 路由
60. [📡 API - sell-point-1](#📡-api---sell-point-1) - 2 路由
61. [📡 API - service-health](#📡-api---service-health) - 1 路由
62. [📡 API - signals](#📡-api---signals) - 4 路由
63. [📡 API - star-system](#📡-api---star-system) - 2 路由
64. [📡 API - stats](#📡-api---stats) - 1 路由
65. [📡 API - sub-account](#📡-api---sub-account) - 4 路由
66. [📡 API - support-resistance](#📡-api---support-resistance) - 12 路由
67. [📡 API - symbol](#📡-api---symbol) - 3 路由
68. [📡 API - system](#📡-api---system) - 3 路由
69. [📡 API - system-role](#📡-api---system-role) - 4 路由
70. [📡 API - telegram](#📡-api---telegram) - 13 路由
71. [📡 API - timeline](#📡-api---timeline) - 1 路由
72. [📡 API - trading](#📡-api---trading) - 6 路由
73. [📡 API - trading-signals](#📡-api---trading-signals) - 3 路由
74. [📡 API - trigger-folder-update](#📡-api---trigger-folder-update) - 1 路由
75. [📡 API - v1v2](#📡-api---v1v2) - 3 路由
76. [🚨 Major Events System](#🚨-major-events-system) - 3 路由

---

## 🌐 Web Pages

**路由数量**: 83

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/aligned-data-view` | GET | `aligned_data_view()` |
| 2 | `/anchor-system` | GET | `anchor_system()` |
| 3 | `/anchor-system-paper` | GET | `anchor_system_paper()` |
| 4 | `/anchor-system-real` | GET | `anchor_system_real()` |
| 5 | `/anchor-system-v2` | GET | `anchor_system_v2()` |
| 6 | `/anchor-test` | GET | `anchor_test()` |
| 7 | `/backfill-monitor` | GET | `backfill_monitor()` |
| 8 | `/cache-help` | GET | `cache_help()` |
| 9 | `/chart` | GET | `chart_page()` |
| 10 | `/chart/<symbol>` | GET | `chart_new()` |
| 11 | `/clear-cache` | GET | `clear_cache_redirect()` |
| 12 | `/clear-cache-guide` | GET | `clear_cache_guide()` |
| 13 | `/coin-change-tracker` | GET | `coin_change_tracker_page()` |
| 14 | `/coin-pool` | GET | `coin_pool_page()` |
| 15 | `/coin-price-history` | GET | `coin_price_history()` |
| 16 | `/coin-price-tracker` | GET | `coin_price_tracker()` |
| 17 | `/coin-tracker-simple` | GET | `coin_tracker_simple()` |
| 18 | `/coin-tracker-v2` | GET | `coin_price_tracker_v2()` |
| 19 | `/control-center` | GET | `control_center_page()` |
| 20 | `/crypto-index` | GET | `crypto_index_page()` |
| 21 | `/daily-tasks-status` | GET | `daily_tasks_status_page()` |
| 22 | `/data-health-monitor` | GET | `data_health_monitor_page()` |
| 23 | `/depth-chart` | GET | `depth_chart_page()` |
| 24 | `/depth-score` | GET | `depth_score_page()` |
| 25 | `/diagnostic` | GET | `diagnostic()` |
| 26 | `/escape-signal-simple` | GET | `escape_signal_simple_page()` |
| 27 | `/extreme-debug` | GET | `extreme_debug_page()` |
| 28 | `/extreme-tracking` | GET | `extreme_tracking_page()` |
| 29 | `/favicon.ico` | GET | `favicon()` |
| 30 | `/folder-update-monitor` | GET | `folder_update_monitor()` |
| 31 | `/force-refresh` | GET | `force_refresh_page()` |
| 32 | `/fund-monitor` | GET | `fund_monitor_page()` |
| 33 | `/fund-monitor-history` | GET | `fund_monitor_history_page()` |
| 34 | `/gdrive-config` | GET | `gdrive_config()` |
| 35 | `/gdrive-config` | GET | `gdrive_config_page()` |
| 36 | `/gdrive-detector` | GET | `gdrive_detector_page()` |
| 37 | `/gdrive-detector-fresh` | GET | `gdrive_detector_fresh()` |
| 38 | `/gdrive-monitor-status` | GET | `gdrive_monitor_status_page()` |
| 39 | `/monitor` | GET | `monitor_page()` |
| 40 | `/monitor-charts` | GET | `monitor_charts_page()` |
| 41 | `/monitor-old` | GET | `monitor_page_old()` |
| 42 | `/okx-accounts` | GET | `okx_accounts_page()` |
| 43 | `/okx-trading` | GET | `okx_trading()` |
| 44 | `/opening-logic` | GET | `opening_logic_page()` |
| 45 | `/panic` | GET | `panic_page()` |
| 46 | `/popup-demo` | GET | `popup_demo()` |
| 47 | `/position-system` | GET | `position_system()` |
| 48 | `/price-comparison` | GET | `price_comparison_page()` |
| 49 | `/price-speed-monitor` | GET | `price_speed_monitor()` |
| 50 | `/query` | GET | `query_page()` |
| 51 | `/query-test` | GET | `query_test()` |
| 52 | `/sar-bias-trend` | GET | `sar_bias_trend_page()` |
| 53 | `/score-overview` | GET | `score_overview_page()` |
| 54 | `/signals` | GET | `signals_page()` |
| 55 | `/simple-test` | GET | `simple_test()` |
| 56 | `/star-system` | GET | `star_system_page()` |
| 57 | `/status` | GET | `status_page()` |
| 58 | `/support-resistance` | GET | `support_resistance_page()` |
| 59 | `/system-config` | GET | `system_config_page()` |
| 60 | `/system-status` | GET | `system_status()` |
| 61 | `/telegram-dashboard` | GET | `telegram_dashboard()` |
| 62 | `/telegram-notification-settings` | GET | `telegram_notification_settings_page()` |
| 63 | `/test-anchor-chart` | GET | `test_anchor_chart()` |
| 64 | `/test-anchor-markpoint` | GET | `test_anchor_markpoint()` |
| 65 | `/test-btc-eth` | GET | `test_btc_eth()` |
| 66 | `/test-chart` | GET | `test_chart()` |
| 67 | `/test-gdrive-status` | GET | `test_gdrive_status()` |
| 68 | `/test-inline` | GET | `test_inline()` |
| 69 | `/test-positions` | GET | `test_positions_page()` |
| 70 | `/test-profit-chart` | GET | `test_profit_chart()` |
| 71 | `/test-refresh` | GET | `test_refresh()` |
| 72 | `/test-simple` | GET | `test_simple()` |
| 73 | `/test-support-api` | GET | `test_support_api_page()` |
| 74 | `/test-xlm-data` | GET | `test_xlm_data()` |
| 75 | `/timeline` | GET | `timeline_page()` |
| 76 | `/trading-decision` | GET | `trading_decision_page()` |
| 77 | `/trading-signals` | GET | `trading_signals_page()` |
| 78 | `/unified-monitor` | GET | `unified_monitor()` |
| 79 | `/unified-monitor-enhanced` | GET | `monitor_enhanced()` |
| 80 | `/v1v2-monitor` | GET | `v1v2_monitor()` |
| 81 | `/v1v2-settings` | GET | `v1v2_settings()` |
| 82 | `/v1v2-volume` | GET | `v1v2_volume()` |
| 83 | `/warning-test` | GET | `warning_test()` |


## 🎯 Live Trading

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/live-trading` | GET | `live_trading()` |
| 2 | `/live-trading/<path:filename>` | GET | `live_trading_static()` |


## 🏠 Root/Homepage

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/` | GET | `index()` |


## 💰 Symbol Pages

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/symbol/<symbol>` | GET | `symbol_detail()` |
| 2 | `/symbol/<symbol>/v6` | GET | `symbol_detail_v6()` |
| 3 | `/symbol/<symbol>/v7` | GET | `symbol_detail_v7()` |
| 4 | `/symbol/<symbol>/v8` | GET | `symbol_detail_v8()` |


## 📈 K-Line Charts

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/kline-indicators` | GET | `kline_indicators_page()` |
| 2 | `/kline/<symbol>` | GET | `kline_chart()` |


## 📊 SAR Slope System

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/sar-slope` | GET | `sar_slope_page()` |
| 2 | `/sar-slope/<symbol>` | GET | `sar_slope_detail()` |
| 3 | `/sar-slope/bias-chart` | GET | `sar_bias_chart()` |
| 4 | `/sar-slope/chart` | GET | `sar_slope_chart()` |


## 📡 API - aligned-data

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/aligned-data/history` | GET | `api_aligned_data_history()` |


## 📡 API - anchor-profit

**路由数量**: 6

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/anchor-profit/by-date` | GET | `get_anchor_profit_by_date()` |
| 2 | `/api/anchor-profit/collect` | POST | `trigger_anchor_profit_collect()` |
| 3 | `/api/anchor-profit/dates` | GET | `get_anchor_profit_dates()` |
| 4 | `/api/anchor-profit/history` | GET | `get_anchor_profit_history()` |
| 5 | `/api/anchor-profit/latest` | GET | `get_anchor_profit_latest()` |
| 6 | `/api/anchor-profit/summary` | GET | `get_anchor_profit_summary()` |


## 📡 API - anchor-system

**路由数量**: 15

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/anchor-system/alerts` | GET | `get_anchor_alerts()` |
| 2 | `/api/anchor-system/auto-maintenance-config` | GET | `get_auto_maintenance_config()` |
| 3 | `/api/anchor-system/auto-maintenance-config` | POST | `update_auto_maintenance_config()` |
| 4 | `/api/anchor-system/cleanup-extremes` | POST | `cleanup_extreme_records()` |
| 5 | `/api/anchor-system/correction-log` | GET | `get_correction_log()` |
| 6 | `/api/anchor-system/current-positions` | GET | `get_current_positions()` |
| 7 | `/api/anchor-system/extreme-stats` | GET | `get_extreme_stats()` |
| 8 | `/api/anchor-system/extreme-values` | GET | `get_anchor_extreme_values()` |
| 9 | `/api/anchor-system/monitors` | GET | `get_anchor_monitors()` |
| 10 | `/api/anchor-system/profit-history` | GET | `get_anchor_system_profit_history()` |
| 11 | `/api/anchor-system/profit-records` | GET | `get_anchor_profit_records()` |
| 12 | `/api/anchor-system/profit-records-with-coins` | GET | `get_profit_records_with_coins()` |
| 13 | `/api/anchor-system/status` | GET | `get_anchor_status()` |
| 14 | `/api/anchor-system/sub-account-positions` | GET | `get_sub_account_positions()` |
| 15 | `/api/anchor-system/warnings` | GET | `get_anchor_warnings()` |


## 📡 API - backfill-monitor

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/backfill-monitor/logs` | GET | `backfill_monitor_logs()` |
| 2 | `/api/backfill-monitor/stop` | POST | `backfill_monitor_stop()` |


## 📡 API - cache

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/cache/clear` | POST | `cache_clear()` |
| 2 | `/api/cache/stats` | GET | `cache_stats()` |


## 📡 API - chart

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/chart` | GET | `api_chart()` |


## 📡 API - chart-config

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/chart-config` | GET | `chart_config()` |


## 📡 API - coin-change-tracker

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/coin-change-tracker/baseline` | GET | `get_coin_change_baseline()` |
| 2 | `/api/coin-change-tracker/history` | GET | `get_coin_change_history()` |
| 3 | `/api/coin-change-tracker/latest` | GET | `get_coin_change_latest()` |
| 4 | `/api/coin-change-tracker/reset-baseline` | POST | `reset_coin_change_baseline()` |


## 📡 API - coin-price-tracker

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/coin-price-tracker/history` | GET | `api_coin_price_tracker_history()` |
| 2 | `/api/coin-price-tracker/latest` | GET | `api_coin_price_tracker_latest()` |


## 📡 API - coins

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/coins/realtime-status` | GET | `api_coins_realtime_status()` |


## 📡 API - collectors

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/collectors/status` | GET | `api_collectors_status()` |


## 📡 API - count

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/count/am2` | GET | `api_count_am2()` |


## 📡 API - daily-tasks

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/daily-tasks/logs` | GET | `api_daily_tasks_logs()` |
| 2 | `/api/daily-tasks/status` | GET | `api_daily_tasks_status()` |


## 📡 API - data-health-monitor

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/data-health-monitor/logs` | GET | `data_health_monitor_logs()` |
| 2 | `/api/data-health-monitor/restart` | POST | `data_health_monitor_restart()` |
| 3 | `/api/data-health-monitor/service-logs` | GET | `data_health_monitor_service_logs()` |
| 4 | `/api/data-health-monitor/status` | GET | `data_health_monitor_status()` |


## 📡 API - depth-chart-data

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/depth-chart-data` | GET | `api_depth_chart_data()` |


## 📡 API - depth-scores

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/depth-scores` | GET | `api_depth_scores()` |


## 📡 API - escape-signal-simple

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/escape-signal-simple` | GET | `api_escape_signal_simple()` |


## 📡 API - escape-signal-stats

**路由数量**: 7

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/escape-signal-stats` | GET | `api_escape_signal_stats()` |
| 2 | `/api/escape-signal-stats/by-date` | GET | `get_escape_signal_by_date()` |
| 3 | `/api/escape-signal-stats/dates` | GET | `get_escape_signal_dates()` |
| 4 | `/api/escape-signal-stats/incremental` | GET | `api_escape_signal_stats_incremental()` |
| 5 | `/api/escape-signal-stats/keypoints` | GET | `api_escape_signal_stats_keypoints()` |
| 6 | `/api/escape-signal-stats/keypoints-monthly` | GET | `get_escape_signal_keypoints_monthly()` |
| 7 | `/api/escape-signal-stats/summary` | GET | `get_escape_signal_summary()` |


## 📡 API - extreme-market-alerts

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/extreme-market-alerts/latest` | GET | `api_extreme_market_alerts_latest()` |
| 2 | `/api/extreme-market-alerts/stats` | GET | `api_extreme_market_alerts_stats()` |


## 📡 API - extreme-tracking

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/extreme-tracking/snapshot/<snapshot_id>` | GET | `api_extreme_tracking_snapshot_detail()` |
| 2 | `/api/extreme-tracking/snapshots` | GET | `api_extreme_tracking_snapshots()` |
| 3 | `/api/extreme-tracking/stats` | GET | `api_extreme_tracking_stats()` |


## 📡 API - fear-greed

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/fear-greed/history` | GET | `api_fear_greed_history()` |
| 2 | `/api/fear-greed/latest` | GET | `api_fear_greed_latest()` |
| 3 | `/api/fear-greed/statistics` | GET | `api_fear_greed_statistics()` |


## 📡 API - folder-update-status

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/folder-update-status` | GET | `api_folder_update_status()` |


## 📡 API - fund-monitor

**路由数量**: 7

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/fund-monitor/abnormal` | GET | `fund_monitor_abnormal()` |
| 2 | `/api/fund-monitor/abnormal-dates` | GET | `fund_monitor_abnormal_dates()` |
| 3 | `/api/fund-monitor/abnormal-history` | GET | `fund_monitor_abnormal_history()` |
| 4 | `/api/fund-monitor/abnormal-timeline` | GET | `fund_monitor_abnormal_timeline()` |
| 5 | `/api/fund-monitor/config` | GET, POST | `fund_monitor_config()` |
| 6 | `/api/fund-monitor/history/<symbol>` | GET | `fund_monitor_history()` |
| 7 | `/api/fund-monitor/latest` | GET | `fund_monitor_latest()` |


## 📡 API - gdrive-config

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/gdrive-config/get` | GET | `gdrive_config_get()` |
| 2 | `/api/gdrive-config/latest-data` | GET | `gdrive_latest_data()` |
| 3 | `/api/gdrive-config/manual-trigger` | POST | `gdrive_manual_trigger()` |
| 4 | `/api/gdrive-config/update` | POST | `gdrive_config_update()` |


## 📡 API - gdrive-detector

**路由数量**: 6

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/gdrive-detector/config` | GET | `gdrive_detector_get_config()` |
| 2 | `/api/gdrive-detector/config` | POST | `gdrive_detector_update_config()` |
| 3 | `/api/gdrive-detector/logs` | GET | `gdrive_detector_logs()` |
| 4 | `/api/gdrive-detector/status` | GET | `gdrive_detector_status()` |
| 5 | `/api/gdrive-detector/trigger-update` | POST | `gdrive_detector_trigger_update()` |
| 6 | `/api/gdrive-detector/txt-files` | GET | `gdrive_detector_txt_files()` |


## 📡 API - gdrive-monitor

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/gdrive-monitor/status` | GET | `api_gdrive_monitor_status()` |


## 📡 API - get-update-log

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/get-update-log` | GET | `api_get_update_log()` |


## 📡 API - health

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/health` | GET | `api_health()` |


## 📡 API - homepage

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/homepage/summary` | GET | `api_homepage_summary()` |


## 📡 API - index

**路由数量**: 5

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/index/components` | GET | `api_index_components()` |
| 2 | `/api/index/current` | GET | `api_index_current()` |
| 3 | `/api/index/history` | GET | `api_index_history()` |
| 4 | `/api/index/klines` | GET | `api_index_klines()` |
| 5 | `/api/index/start` | POST | `api_index_start()` |


## 📡 API - kline-indicators

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/kline-indicators/collector-status` | GET | `api_kline_indicators_status()` |
| 2 | `/api/kline-indicators/latest` | GET | `api_kline_indicators_latest()` |
| 3 | `/api/kline-indicators/signals` | GET | `api_kline_indicators_signals()` |


## 📡 API - kline-indicators-tv

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/kline-indicators-tv/collector-status` | GET | `api_kline_indicators_tv_status()` |
| 2 | `/api/kline-indicators-tv/latest` | GET | `api_kline_indicators_tv_latest()` |


## 📡 API - latest

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/latest` | GET | `api_latest()` |


## 📡 API - liquidation

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/liquidation/30days` | GET | `api_liquidation_30days()` |


## 📡 API - liquidation-1h

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/liquidation-1h/history` | GET | `api_liquidation_1h_history()` |
| 2 | `/api/liquidation-1h/latest` | GET | `api_liquidation_1h_latest()` |


## 📡 API - list-recent-folders

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/list-recent-folders` | GET | `api_list_recent_folders()` |


## 📡 API - live-trading

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/live-trading/<path:endpoint>` | GET, POST, PUT, DELETE | `live_trading_api()` |


## 📡 API - major-events

**路由数量**: 5

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/major-events/current-status` | GET | `get_major_events_status()` |
| 2 | `/api/major-events/data/liquidation` | GET | `get_liquidation_data()` |
| 3 | `/api/major-events/data/sar-slope` | GET | `get_sar_slope_data()` |
| 4 | `/api/major-events/recent` | GET | `get_recent_major_events()` |
| 5 | `/api/major-events/trigger-check` | POST | `trigger_event_check()` |


## 📡 API - market-average-score

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/market-average-score` | GET | `api_market_average_score()` |


## 📡 API - modules

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/modules/stats` | GET | `api_modules_stats()` |


## 📡 API - monitor

**路由数量**: 8

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/monitor/all-modules` | GET | `api_monitor_all_modules()` |
| 2 | `/api/monitor/check` | POST | `api_monitor_check()` |
| 3 | `/api/monitor/check-all` | POST | `api_monitor_check_all()` |
| 4 | `/api/monitor/data-collection` | GET | `api_monitor_data_collection()` |
| 5 | `/api/monitor/force-update/<module_key>` | POST | `api_monitor_force_update()` |
| 6 | `/api/monitor/history` | GET | `api_monitor_history()` |
| 7 | `/api/monitor/status` | GET | `api_monitor_status()` |
| 8 | `/api/monitor/trigger` | POST | `api_monitor_trigger()` |


## 📡 API - okex-crypto-index

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/okex-crypto-index` | GET | `api_okex_crypto_index()` |


## 📡 API - okx-accounts

**路由数量**: 5

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/okx-accounts/<account_id>` | GET | `okx_account_detail()` |
| 2 | `/api/okx-accounts/list` | GET | `okx_accounts_list()` |
| 3 | `/api/okx-accounts/list-with-credentials` | GET | `okx_accounts_list_with_credentials()` |
| 4 | `/api/okx-accounts/set-default/<account_id>` | POST | `okx_set_default_account()` |
| 5 | `/api/okx-accounts/update-status/<account_id>` | POST | `okx_update_account_status()` |


## 📡 API - okx-day-change

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/okx-day-change/history` | GET | `api_okx_day_change_history()` |
| 2 | `/api/okx-day-change/latest` | GET | `api_okx_day_change_latest()` |


## 📡 API - okx-trading

**路由数量**: 15

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/okx-trading/account-balance` | POST | `get_okx_account_balance()` |
| 2 | `/api/okx-trading/account-info` | POST | `get_okx_account_info()` |
| 3 | `/api/okx-trading/batch-order` | POST | `batch_order_from_event()` |
| 4 | `/api/okx-trading/cancel-order` | POST | `cancel_okx_order()` |
| 5 | `/api/okx-trading/close-position` | POST | `close_okx_position()` |
| 6 | `/api/okx-trading/favorite-symbols` | GET | `get_favorite_symbols()` |
| 7 | `/api/okx-trading/favorite-symbols` | POST | `update_favorite_symbols()` |
| 8 | `/api/okx-trading/hedge-order` | POST | `hedge_order_from_event()` |
| 9 | `/api/okx-trading/logs` | GET | `get_okx_trading_logs()` |
| 10 | `/api/okx-trading/market-tickers` | GET | `get_okx_market_tickers()` |
| 11 | `/api/okx-trading/order-detail` | POST | `get_okx_order_detail()` |
| 12 | `/api/okx-trading/pending-orders` | POST | `get_okx_pending_orders()` |
| 13 | `/api/okx-trading/place-order` | POST | `place_okx_order()` |
| 14 | `/api/okx-trading/positions` | POST | `get_okx_positions()` |
| 15 | `/api/okx-trading/set-tpsl` | POST | `set_okx_tpsl()` |


## 📡 API - opening-logic

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/opening-logic/suggestion` | GET | `opening_logic_suggestion()` |


## 📡 API - pair-protection

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/pair-protection/check` | POST | `manual_check_protection()` |
| 2 | `/api/pair-protection/start` | POST | `start_pair_protection()` |
| 3 | `/api/pair-protection/status` | GET | `get_pair_protection_status()` |
| 4 | `/api/pair-protection/stop` | POST | `stop_pair_protection()` |


## 📡 API - panic

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/panic/30d-stats` | GET | `get_panic_30d_stats()` |
| 2 | `/api/panic/history` | GET | `api_panic_history()` |
| 3 | `/api/panic/hour1-curve` | GET | `api_panic_hour1_curve()` |
| 4 | `/api/panic/latest` | GET | `api_panic_latest()` |


## 📡 API - position

**路由数量**: 5

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/position/history/<symbol>` | GET | `api_position_history()` |
| 2 | `/api/position/latest` | GET | `api_position_latest()` |
| 3 | `/api/position/stats/history` | GET | `api_position_stats_history()` |
| 4 | `/api/position/stats/latest` | GET | `api_position_stats_latest()` |
| 5 | `/api/position/summary` | GET | `api_position_summary()` |


## 📡 API - price-comparison

**路由数量**: 5

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/price-comparison/breakthrough-logs` | GET | `api_breakthrough_logs()` |
| 2 | `/api/price-comparison/breakthrough-stats` | GET | `api_breakthrough_stats()` |
| 3 | `/api/price-comparison/list` | GET | `api_price_comparison_list()` |
| 4 | `/api/price-comparison/update` | POST | `api_price_comparison_update()` |
| 5 | `/api/price-comparison/update-ratios` | GET | `api_update_price_ratios()` |


## 📡 API - price-speed

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/price-speed/history/<symbol>` | GET | `api_price_speed_history()` |
| 2 | `/api/price-speed/latest` | GET | `api_price_speed_latest()` |


## 📡 API - query

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/query` | GET | `api_query()` |
| 2 | `/api/query/batch-import` | POST | `api_query_batch_import()` |
| 3 | `/api/query/latest` | GET | `api_query_latest()` |


## 📡 API - sar-slope

**路由数量**: 21

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/sar-slope/1min-data` | GET | `sar_1min_data()` |
| 2 | `/api/sar-slope/alerts` | GET | `sar_slope_alerts()` |
| 3 | `/api/sar-slope/bias-ratios` | GET | `sar_slope_bias_ratios_batch()` |
| 4 | `/api/sar-slope/bias-stats` | GET | `sar_bias_stats()` |
| 5 | `/api/sar-slope/bias-stats/history` | GET | `api_sar_bias_stats_history()` |
| 6 | `/api/sar-slope/bias-stats/latest` | GET | `api_sar_bias_stats_latest()` |
| 7 | `/api/sar-slope/bias-trend` | GET | `sar_slope_bias_trend()` |
| 8 | `/api/sar-slope/bias-trend-by-date` | GET | `sar_slope_bias_trend_by_date()` |
| 9 | `/api/sar-slope/collector-status` | GET | `api_sar_slope_collector_status()` |
| 10 | `/api/sar-slope/conversions` | GET | `sar_slope_conversions()` |
| 11 | `/api/sar-slope/current-cycle/<symbol>` | GET | `sar_slope_current_cycle_jsonl()` |
| 12 | `/api/sar-slope/duration-signal/<symbol>` | GET | `sar_slope_duration_signal()` |
| 13 | `/api/sar-slope/history/<symbol>` | GET | `api_sar_slope_history()` |
| 14 | `/api/sar-slope/latest` | GET | `api_sar_slope_latest()` |
| 15 | `/api/sar-slope/latest-jsonl` | GET | `sar_slope_latest_jsonl()` |
| 16 | `/api/sar-slope/position-changes/<symbol>` | GET | `api_sar_slope_position_changes()` |
| 17 | `/api/sar-slope/query/<symbol>` | GET | `sar_slope_query_symbol()` |
| 18 | `/api/sar-slope/sequence-compare/<symbol>` | GET | `sar_slope_sequence_compare()` |
| 19 | `/api/sar-slope/status` | GET | `sar_slope_status()` |
| 20 | `/api/sar-slope/symbol/<symbol>` | GET | `sar_slope_symbol_data()` |
| 21 | `/api/sar-slope/transition-analysis/<symbol>` | GET | `sar_slope_transition_analysis()` |


## 📡 API - sell-point-1

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/sell-point-1/latest` | GET | `api_sell_point_1_latest()` |
| 2 | `/api/sell-point-1/save` | POST | `api_sell_point_1_save()` |


## 📡 API - service-health

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/service-health` | GET | `service_health()` |


## 📡 API - signals

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/signals/chart` | GET | `api_signals_chart()` |
| 2 | `/api/signals/history` | GET | `api_signals_history()` |
| 3 | `/api/signals/recent` | GET | `api_signals_recent()` |
| 4 | `/api/signals/stats` | GET | `api_signals_stats()` |


## 📡 API - star-system

**路由数量**: 2

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/star-system/data` | GET | `api_star_system_data()` |
| 2 | `/api/star-system/history` | GET | `api_star_system_history()` |


## 📡 API - stats

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/stats` | GET | `api_stats()` |


## 📡 API - sub-account

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/sub-account/close-all-positions` | POST | `close_all_sub_account_positions()` |
| 2 | `/api/sub-account/close-position` | POST | `close_sub_account_position()` |
| 3 | `/api/sub-account/config` | GET | `get_sub_account_config()` |
| 4 | `/api/sub-account/config` | POST | `update_sub_account_config()` |


## 📡 API - support-resistance

**路由数量**: 12

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/support-resistance/chart-data` | GET | `api_support_resistance_chart_data()` |
| 2 | `/api/support-resistance/dates` | GET | `api_support_resistance_dates()` |
| 3 | `/api/support-resistance/download/<filename>` | GET | `api_support_resistance_download()` |
| 4 | `/api/support-resistance/escape-max-stats` | GET | `api_support_resistance_escape_max_stats()` |
| 5 | `/api/support-resistance/export` | POST | `api_support_resistance_export()` |
| 6 | `/api/support-resistance/import` | POST | `api_support_resistance_import()` |
| 7 | `/api/support-resistance/latest` | GET | `api_support_resistance_latest()` |
| 8 | `/api/support-resistance/latest-from-jsonl` | GET | `api_support_resistance_latest_from_jsonl()` |
| 9 | `/api/support-resistance/latest-signal` | GET | `api_support_resistance_latest_signal()` |
| 10 | `/api/support-resistance/signals-computed` | GET | `api_support_resistance_signals_computed()` |
| 11 | `/api/support-resistance/snapshots` | GET | `api_support_resistance_snapshots()` |
| 12 | `/api/support-resistance/trend` | GET | `api_support_resistance_trend()` |


## 📡 API - symbol

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/symbol/<symbol>/extremes` | GET | `api_symbol_extremes()` |
| 2 | `/api/symbol/<symbol>/indicators` | GET | `api_symbol_indicators()` |
| 3 | `/api/symbol/<symbol>/kline` | GET | `api_symbol_kline()` |


## 📡 API - system

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/system/health-status` | GET | `api_system_health_status()` |
| 2 | `/api/system/role-config` | GET | `api_get_role_config()` |
| 3 | `/api/system/role-config` | POST | `api_update_role_config()` |


## 📡 API - system-role

**路由数量**: 4

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/system-role/config` | GET | `api_system_role_config_get()` |
| 2 | `/api/system-role/config` | POST | `api_system_role_config_post()` |
| 3 | `/api/system-role/health-status` | GET | `api_system_role_health_status()` |
| 4 | `/api/system-role/toggle` | POST | `api_system_role_toggle()` |


## 📡 API - telegram

**路由数量**: 13

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/telegram/config` | GET, POST | `telegram_config_api()` |
| 2 | `/api/telegram/history` | GET | `telegram_history()` |
| 3 | `/api/telegram/notification-config` | GET | `get_telegram_notification_config()` |
| 4 | `/api/telegram/notification-config` | POST | `update_telegram_notification_config()` |
| 5 | `/api/telegram/signals/count-alerts` | GET | `api_telegram_count_alerts()` |
| 6 | `/api/telegram/signals/stats` | GET | `api_telegram_stats()` |
| 7 | `/api/telegram/signals/support-resistance` | GET | `api_telegram_support_resistance()` |
| 8 | `/api/telegram/signals/trading` | GET | `api_telegram_trading()` |
| 9 | `/api/telegram/start` | POST | `api_telegram_start()` |
| 10 | `/api/telegram/status` | GET | `telegram_status()` |
| 11 | `/api/telegram/stop` | POST | `api_telegram_stop()` |
| 12 | `/api/telegram/system/status` | GET | `api_telegram_system_status()` |
| 13 | `/api/telegram/webhook` | POST | `telegram_webhook()` |


## 📡 API - timeline

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/timeline` | GET | `api_timeline()` |


## 📡 API - trading

**路由数量**: 6

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/trading/anchor-maintenance/logs` | GET | `anchor_maintenance_logs_api()` |
| 2 | `/api/trading/config` | GET, POST | `trading_config_api()` |
| 3 | `/api/trading/decisions` | GET | `trading_decisions_api()` |
| 4 | `/api/trading/maintenance` | GET | `trading_maintenance_api()` |
| 5 | `/api/trading/positions/opens` | GET | `get_trading_positions_opens()` |
| 6 | `/api/trading/signals` | GET | `trading_signals_api()` |


## 📡 API - trading-signals

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/trading-signals/analyze` | GET | `api_trading_signals_analyze()` |
| 2 | `/api/trading-signals/buy-points` | GET | `api_trading_signals_buy_points()` |
| 3 | `/api/trading-signals/history` | GET | `api_trading_signals_history()` |


## 📡 API - trigger-folder-update

**路由数量**: 1

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/trigger-folder-update` | POST | `api_trigger_folder_update()` |


## 📡 API - v1v2

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/api/v1v2/latest` | GET | `api_v1v2_latest()` |
| 2 | `/api/v1v2/settings` | GET, POST | `api_v1v2_settings()` |
| 3 | `/api/v1v2/statistics` | GET | `api_v1v2_statistics()` |


## 🚨 Major Events System

**路由数量**: 3

| # | 路由路径 | HTTP方法 | 函数名 |
|---|---------|---------|--------|
| 1 | `/major-events` | GET | `major_events_page()` |
| 2 | `/major-events-test` | GET | `major_events_test()` |
| 3 | `/major-events/<path:filename>` | GET | `major_events_static()` |

