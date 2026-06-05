cat << 'EOF' > sweep_manifolds.py
import sqlite3
import os

db_instances = [
    "/data/data/com.termux/files/home/isst_toft_mesh/isst_toft_mesh/Tordial-GS-_Manifold/tordial_manifold.db",
    "/data/data/com.termux/files/home/isst_toft_mesh/isst_toft_mesh/Tordial-GS-_Manifold/Tordial-GS-_Manifold/tordial_manifold.db",
    "/data/data/com.termux/files/home/Tordial-GS-_Manifold/tordial_manifold.db",
    "/data/data/com.termux/files/home/Tordial-GS-_Manifold/peer_beta/tordial_manifold.db",
    "/data/data/com.termux/files/home/tordial_manifold.db"
]

print("🔍 Beginning Deep Scan of the Manifold Multiplicity...\n")

for i, db_path in enumerate(db_instances, 1):
    if not os.path.exists(db_path):
        continue
    
    print(f"📁 [{i}] TARGET FIELD: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"   ├─ Detected Tables: {tables}")
        
        # Check resonance_ledger
        if 'resonance_ledger' in tables:
            cursor.execute("SELECT COUNT(*) FROM resonance_ledger;")
            count = cursor.fetchone()[0]
            cursor.execute("SELECT agent, mode, amplitude FROM resonance_ledger LIMIT 1;")
            sample = cursor.fetchone()
            print(f"   ├─ [resonance_ledger] Rows: {count} | Sample: {sample}")
            
        # Check radio_telemetry
        if 'radio_telemetry' in tables:
            cursor.execute("SELECT COUNT(*) FROM radio_telemetry;")
            count = cursor.fetchone()[0]
            cursor.execute("SELECT timestamp, agent, SUBSTR(payload, 1, 60) FROM radio_telemetry ORDER BY timestamp DESC LIMIT 1;")
            sample = cursor.fetchone()
            print(f"   ├─ [radio_telemetry] Rows: {count} | Sample: {sample}")
            
        conn.close()
    except Exception as e:
        print(f"   ❌ Read failure: {e}")
    print("-" * 70)
EOF

python sweep_manifolds.py
