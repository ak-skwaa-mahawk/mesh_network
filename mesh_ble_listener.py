cat << 'EOF' > mesh_ble_listener.py
import meshtastic.ble_interface
import sys

# Replace this string template with the true MAC address found in step 2
target_mac = "XX:XX:XX:XX:XX:XX" 

print(f"Connecting to hardware mesh matrix via BLE link: {target_mac}...")
try:
    interface = meshtastic.ble_interface.BLEInterface(address=target_mac)
    my_nodes = interface.getNodes()
    print("\n🔒 Off-Grid Mesh Topology Decoded:")
    print(my_nodes)
    interface.close()
except Exception as e:
    print(f"❌ Connection dropped: {e}")
EOF
