cat << 'EOF' > mesh_network_listener.py
import meshtastic.tcp_interface
import time

target_ip = "192.168.1.X"  # <--- Shift to your real hardware IP address

print(f"Connecting to off-grid mesh backplane via TCP target: {target_ip}...")
try:
    # Initialize an explicit socket connection completely bypassing serial ports
    interface = meshtastic.tcp_interface.TCPInterface(hostname=target_ip)
    
    # Pull the local hardware profile metadata info
    my_info = interface.getNodes()
    print("\n🔒 Node Network Topology Discovered:")
    print(my_info)
    
    interface.close()
except Exception as e:
    print(f"❌ Connection anomaly: {e}")
EOF

# Execute the pure socket bridge
python mesh_network_listener.py
