/*
intent_tracker.rs
Manages tight invariant parameter sets and bounds diagnostics.
*/

use rusqlite::Connection;

pub struct IntentParams {
    pub imax_per_mode: f64,
    pub didt_max: f64,
    pub decay_halflife_ms: u64,
}

pub struct SqliteIntentStore {
    conn: Connection,
}

impl SqliteIntentStore {
    pub fn new(conn: Connection) -> Result<Self, rusqlite::Error> {
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
