cat << 'EOF' > mesh_to_ledger_bridge.py
import meshtastic.tcp_interface
import sqlite3
import sys
import json

target_ip = "192.168.42.1"
db_path = "tordial_manifold.db"

print("🚀 Launching Sovereign Mesh-to-Ledger Bridge Automation...")

try:
    # 1. Connect directly to the node's local network gateway
    print(f"🔗 Dialing target interface: {target_ip}...")
    interface = meshtastic.tcp_interface.TCPInterface(hostname=target_ip)
    
    # 2. Extract configuration metadata matrix
    nodes = interface.getNodes()
    interface.close()
    
    if not nodes:
        print("⚠️ Warning: Received empty node dictionary from mesh backplane.")
        sys.exit(1)
        
    print("✅ Radio node packet ingested successfully.")
    
    # Clean string conversion avoiding illegal keyword arguments
    serialized_mesh = json.dumps(nodes, default=str)

    # 3. Commit variables directly to your persistent storage matrix
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS radio_telemetry (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent TEXT,
            payload TEXT
        )
    """)
    
    cursor.execute(
        "INSERT INTO radio_telemetry (agent, payload) VALUES (?, ?)",
        ("MESHTASTIC_AP", serialized_mesh)
    )
    
    conn.commit()
    conn.close()
    print("🔒 Mesh network coordinates safely written to tordial_manifold.db.")

except Exception as e:
    print(f"❌ Automation anomaly: {e}")
EOF
