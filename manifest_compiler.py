#!/data/data/com.termux/files/usr/bin/python3
import sys
import json
from pathlib import Path
from archinstall.lib.models import Size, SectorSize, Unit, SubvolumeModification

PROFILES = {
    "handheld_gaming": {
        "description": "Optimized for Steam Deck / ROG Ally / x86 handhelds (Btrfs + compress=zstd)",
        "disk": "/dev/nvme0n1",
        "esp_size_mib": 1024,
        "root_subvols": ["@", "@home", "@games", "@snapshots", "@var_log"],
        "mount_options": ["compress=zstd:3", "noatime", "discard=async"]
    },
    "edge_node": {
        "description": "Lightweight mesh node / headless appliance (ext4 / robust failover)",
        "disk": "/dev/sda",
        "esp_size_mib": 512,
        "root_subvols": None,
        "fs_type": "ext4",
        "mount_options": ["noatime"]
    },
    "workstation_luks": {
        "description": "High-capacity workstation with isolated snapshot layout",
        "disk": "/dev/nvme0n1",
        "esp_size_mib": 2048,
        "root_subvols": ["@", "@home", "@cache", "@snapshots"],
        "mount_options": ["compress=zstd:1", "space_cache=v2"]
    }
}

def generate_disk_spec(profile_key, total_gib=512):
    if profile_key not in PROFILES:
        raise ValueError(f"Unknown profile: {profile_key}. Available: {list(PROFILES.keys())}")
    
    spec = PROFILES[profile_key]
    sec = SectorSize.default()
    
    esp_size = spec["esp_size_mib"]
    p1_start = Size(1, Unit.MiB, sec).json()
    p1_size = Size(esp_size, Unit.MiB, sec).json()
    
    # 1 MiB start alignment + headroom reserved at tail for backup GPT
    root_start_mib = esp_size + 1
    root_size_gib = total_gib - (esp_size // 1024) - 2
    
    p2_start = Size(root_start_mib, Unit.MiB, sec).json()
    p2_size = Size(root_size_gib, Unit.GiB, sec).json()
    
    partitions = [
        {
            "status": "create",
            "type": "boot",
            "start": p1_start,
            "size": p1_size,
            "fs_type": "fat32",
            "mountpoint": "/boot",
            "mount_options": ["fmask=0077", "dmask=0077"],
            "flags": ["boot"],
            "dev_path": None,
            "obj_id": "esp_part"
        }
    ]
    
    if spec.get("root_subvols"):
        subvols = []
        for name in spec["root_subvols"]:
            mp = "/" if name == "@" else f"/{name.replace('@', '')}"
            subvols.append(SubvolumeModification(name=name, mountpoint=mp).json())
            
        partitions.append({
            "status": "create",
            "type": "primary",
            "start": p2_start,
            "size": p2_size,
            "fs_type": "btrfs",
            "mountpoint": "/",
            "mount_options": spec["mount_options"],
            "flags": [],
            "dev_path": None,
            "obj_id": "root_part",
            "btrfs": subvols
        })
    else:
        partitions.append({
            "status": "create",
            "type": "primary",
            "start": p2_start,
            "size": p2_size,
            "fs_type": spec["fs_type"],
            "mountpoint": "/",
            "mount_options": spec["mount_options"],
            "flags": [],
            "dev_path": None,
            "obj_id": "root_part"
        })
        
    return {
        "config_type": "manual_partitioning",
        "device_modifications": [
            {
                "device": spec["disk"],
                "wipe": True,
                "partitions": partitions
            }
        ]
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "handheld_gaming"
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 512
    manifest = generate_disk_spec(target, size)
    
    out_file = Path(f"{target}_manifest.json")
    out_file.write_text(json.dumps(manifest, indent=2))
    print(f"[+] Compiled '{target}' ({size} GiB) -> {out_file}")
