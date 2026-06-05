cat << 'EOF' > mesh_serial_listener.py
import serial
import sys

# Standard Android/Termux USB serial port endpoints
possible_ports = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/bus/usb/001/002']

print("🔌 Probing physical serial interface lines...")
stream = None

for port in possible_ports:
    try:
        # Latch directly onto the hardware serial line at standard baudrate
        stream = serial.Serial(port, 921600, timeout=2)
        print(f"✅ HARDWARE BOUND: Pumping data from {port}")
        break
    except Exception:
        continue

if not stream:
    print("❌ No direct serial stream found. Verify USB-OTG connection permissions.")
    sys.exit(1)

try:
    while True:
        # Ingest raw off-grid telemetry frames as they cross the airwaves
        data = stream.readline()
        if data:
            print(f"📡 [MESH FRAME]: {data.decode('utf-8', errors='ignore').strip()}")
except KeyboardInterrupt:
    print("\n🔒 Pipeline disconnected.")
    stream.close()
EOF

# Execute the direct serial ingestion channel
python mesh_serial_listener.py
