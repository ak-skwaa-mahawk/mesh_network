import meshtastic.tcp_interface
import sqlite3
import sys
import json

target_ip = "192.168.42.1"
db_path = "/data/data/com.termux/files/home/tordial_manifold.db"

print("🚀 Launching Sovereign Mesh-to-Ledger Bridge Automation...")

try:
    print(f"🔗 Dialing target interface: {target_ip}...")
    interface = meshtastic.tcp_interface.TCPInterface(hostname=target_ip)

    nodes = interface.getNodes()
    interface.close()

    if not nodes:
        print("⚠️ Warning: Received empty node dictionary from mesh backplane.")
        sys.exit(1)

    print("✅ Radio node packet ingested successfully.")
    serialized_mesh = json.dumps(nodes, default=str)

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
