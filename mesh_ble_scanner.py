cat << 'EOF' > mesh_ble_scanner.py
import asyncio
from bleak import BleakScanner

async def main():
    print("📡 Sniffing local airwaves for off-grid BLE radio nodes...")
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name and ("Mesh" in d.name or "Meshtastic" in d.name):
            print(f"🔒 FOUND NODE: {d.name} | MAC Address: {d.address}")
        elif d.name:
            print(f"  Discovered client: {d.name} [{d.address}]")

asyncio.run(main())
EOF
