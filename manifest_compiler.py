#!/data/data/com.termux/files/usr/bin/python3
import sys
import json
from pathlib import Path
from archinstall.lib.disk.device_handler import device_handler
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

def generate_disk_spec(profile_key):
    if profile_key not in PROFILES:
        raise ValueError(f"Unknown profile: {profile_key}. Available: {list(PROFILES.keys())}")

    spec = PROFILES[profile_key]
    target_path = Path(spec["disk"])

    device_handler.load_devices()
    dev = device_handler.get_device(target_path)
    if not dev:
        raise RuntimeError(f"Device {target_path} not found in device_handler. Run set-mock-disk first.")

    sector_size = dev.device_info.sector_size
    total_bytes = dev.device_info.total_size.value
    total_sectors = total_bytes // sector_size.value

    # Standard 1 MiB alignment = 2048 sectors (for 512B sectors)
    align_sectors = (1024 * 1024) // sector_size.value

    # Partition 1: ESP
    esp_start_sec = align_sectors
    esp_size_mib = spec["esp_size_mib"]
    esp_sectors = (esp_size_mib * 1024 * 1024) // sector_size.value

    # Partition 2: Root
    root_start_sec = esp_start_sec + esp_sectors

    # Reserve the final 34 sectors for backup GPT and snap length DOWN to 1 MiB alignment
    max_end_sector = total_sectors - 34
    available_sectors = max_end_sector - root_start_sec
    root_sectors = (available_sectors // align_sectors) * align_sectors

    if root_sectors <= 0:
        raise ValueError("Calculated root partition size is zero or negative.")

    p1_start = Size(esp_start_sec * sector_size.value, Unit.B, sector_size).json()
    p1_size = Size(esp_sectors * sector_size.value, Unit.B, sector_size).json()

    p2_start = Size(root_start_sec * sector_size.value, Unit.B, sector_size).json()
    p2_size = Size(root_sectors * sector_size.value, Unit.B, sector_size).json()

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
    manifest = generate_disk_spec(target)

    out_file = Path(f"{target}_manifest.json")
    out_file.write_text(json.dumps(manifest, indent=2))
    print(f"[+] Compiled '{target}' -> {out_file}")
