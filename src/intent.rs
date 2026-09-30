cat << 'EOF' > src/intent.rs
use rusqlite::{params, Connection, Result};
use std::time::{Duration, Instant};

pub struct IntentParams {
    pub imax_per_mode: f64,
    pub didt_max: f64,
    pub decay_halflife_ms: u64,
}

pub struct SqliteIntentStore {
    conn: Connection,
}

impl SqliteIntentStore {
    pub fn new(conn: Connection) -> Result<Self> {
        conn.execute(
            "CREATE TABLE IF NOT EXISTS resonance_ledger (
                agent TEXT NOT NULL,
                mode TEXT NOT NULL,
                amplitude REAL NOT NULL,
                phase REAL NOT NULL,
                curvature REAL NOT NULL,
                PRIMARY KEY (agent, mode)
            );",
            [],
        )?;
        Ok(SqliteIntentStore { conn })
    }
}

pub struct IntentEngine {
    store: SqliteIntentStore,
    params: IntentParams,
    last_update: Instant,
}

impl IntentEngine {
    pub fn new(store: SqliteIntentStore, params: IntentParams) -> Self {
        IntentEngine {
            store,
            params,
            last_update: Instant::now(),
        }
    }

    pub fn inspect_bounds(&self) {
        println!("🔒 IntentEngine Bound Constraints Active.");
        println!("   ├── Max Saturation (I_max): {}", self.params.imax_per_mode);
        println!("   └── Velocity Delta Limit (dI/dt): {}", self.params.didt_max);
    }
}
EOF
