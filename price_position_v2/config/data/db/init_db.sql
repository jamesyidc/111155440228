-- 价格位置数据库初始化脚本

CREATE TABLE IF NOT EXISTS price_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inst_id TEXT NOT NULL,
    snapshot_time TEXT NOT NULL,
    current_price REAL,
    high_48h REAL,
    low_48h REAL,
    position_48h REAL,
    high_7d REAL,
    low_7d REAL,
    position_7d REAL,
    alert_48h_low INTEGER DEFAULT 0,
    alert_48h_high INTEGER DEFAULT 0,
    alert_7d_low INTEGER DEFAULT 0,
    alert_7d_high INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inst_id ON price_positions(inst_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_time ON price_positions(snapshot_time);
CREATE INDEX IF NOT EXISTS idx_inst_time ON price_positions(inst_id, snapshot_time);
