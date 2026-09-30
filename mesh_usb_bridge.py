cat << 'EOF' > mesh_usb_bridge.py
import os
import sys
import serial

print("🔌 Initializing Android File Descriptor Ingestion Layer...")

# Termux passes the raw hardware file descriptor index via standard system args
if len(sys.argv) < 2:
    print("❌ Critical: No hardware file descriptor passed by the Termux shell wrapper.")
    sys.exit(1)

try:
    fd_index = int(sys.argv[1])
    # Open the raw file descriptor natively, bypassing standard /dev/ path checks
    stream = serial.Serial()
    stream.port = f"fd://{fd_index}"
    stream.baudrate = 921600
    stream.timeout = 2
    stream.open()
    
    print(f"✅ HARDWARE BOUND VIA FD {fd_index}. Ingesting live mesh frames...")
    
    while True:
        data = stream.readline()
        if data:
            print(f"📡 [MESH FRAME]: {data.decode('utf-8', errors='ignore').strip()}")
            
except KeyboardInterrupt:
    print("\n🔒 Hardware channel gracefully disconnected.")
except Exception as e:
    print(f"❌ Ingestion anomaly: {e}")
EOF
