#!/bin/bash
# AOCROS Install to Disk Script
# Run from live ISO to install to local disk

set -e

echo "======================================"
echo "  AOCROS Installation"
echo "  Mylzeron + Tappy"
echo "======================================"
echo ""

# Target device (passed as argument or detected)
TARGET_DEVICE="${1:-}"

if [ -z "$TARGET_DEVICE" ]; then
    echo "Available storage devices:"
    lsblk -d -o NAME,SIZE,MODEL | grep -v "loop\|ram"
    echo ""
    read -p "Enter target device (e.g., sda, nvme0n1): " TARGET_DEVICE
fi

TARGET_DEVICE="/dev/${TARGET_DEVICE#/dev/}"

if [ ! -b "$TARGET_DEVICE" ]; then
    echo "Error: $TARGET_DEVICE is not a valid block device"
    exit 1
fi

echo ""
echo "WARNING: This will ERASE ALL DATA on $TARGET_DEVICE"
read -p "Type 'CONFIRM' to proceed: " confirm

if [ "$confirm" != "CONFIRM" ]; then
    echo "Installation cancelled"
    exit 0
fi

# Unmount any existing partitions
umount ${TARGET_DEVICE}* 2>/dev/null || true

echo ""
echo "[1/5] Creating partitions..."

# Create GPT partition table
parted -s $TARGET_DEVICE mklabel gpt

# Partition 1: EFI (512MB)
parted -s $TARGET_DEVICE mkpart ESP fat32 1MiB 513MiB
parted -s $TARGET_DEVICE set 1 boot on

# Partition 2: AOCROS System (4GB minimum, auto)
parted -s $TARGET_DEVICE mkpart primary ext4 513MiB 4.5GiB

# Partition 3: Persistent Storage (rest of disk)
parted -s $TARGET_DEVICE mkpart primary ext4 4.5GiB 100%

# Wait for kernel
sleep 2
partprobe $TARGET_DEVICE 2>/dev/null || true
sleep 1

# Format partitions
echo "[2/5] Formatting partitions..."

EFI_PART="${TARGET_DEVICE}1"
SYS_PART="${TARGET_DEVICE}2"
PERSIST_PART="${TARGET_DEVICE}3"

# Handle nvme naming
if [[ "$TARGET_DEVICE" == *"nvme"* ]]; then
    EFI_PART="${TARGET_DEVICE}p1"
    SYS_PART="${TARGET_DEVICE}p2"
    PERSIST_PART="${TARGET_DEVICE}p3"
fi

mkfs.fat -F32 $EFI_PART
mkfs.ext4 -F $SYS_PART
mkfs.ext4 -F $PERSIST_PART

# Mount points
MOUNT_ROOT=/mnt/aocros-install
mkdir -p $MOUNT_ROOT

echo "[3/5] Installing base system..."
mount $SYS_PART $MOUNT_ROOT

# Create directory structure
mkdir -p $MOUNT_ROOT/{boot,home}
mkdir -p $MOUNT_ROOT/home/{mylzeron,tappy,aocros}

# Copy squashfs contents
echo "  Extracting base system..."
unsquashfs -f -d $MOUNT_ROOT /mnt/usb/boot/base.squashfs 2>/dev/null || {
    # Fallback: copy live system
    echo "  Copying live system..."
    cp -a /bin /lib /lib64 /sbin /usr /etc /var $MOUNT_ROOT/ 2>/dev/null || true
}

# Install kernel
echo "  Installing kernel..."
cp /boot/vmlinuz-* $MOUNT_ROOT/boot/vmlinuz-aocros 2>/dev/null || true
cp /boot/initramfs-* $MOUNT_ROOT/boot/initramfs-aocros.img 2>/dev/null || true

# Create fstab
cat > $MOUNT_ROOT/etc/fstab << 'FSTAB'
# AOCROS fstab
PARTUUID=EFI     /boot/efi       vfat    defaults,noatime 0 2
PARTUUID=SYS     /               ext4    defaults,noatime 0 1
PARTUUID=PERSIST /mnt/persist    ext4    defaults,noatime 0 2
FSTAB

# Update fstab with actual UUIDs
EFI_UUID=$(blkid -s PARTUUID -o value $EFI_PART)
SYS_UUID=$(blkid -s PARTUUID -o value $SYS_PART)
PERSIST_UUID=$(blkid -s PARTUUID -o value $PERSIST_PART)

sed -i "s/PARTUUID=EFI/PARTUUID=$EFI_UUID/" $MOUNT_ROOT/etc/fstab
sed -i "s/PARTUUID=SYS/PARTUUID=$SYS_UUID/" $MOUNT_ROOT/etc/fstab
sed -i "s/PARTUUID=PERSIST/PARTUUID=$PERSIST_UUID/" $MOUNT_ROOT/etc/fstab

echo "[4/5] Installing bootloader..."

# Mount EFI
mkdir -p $MOUNT_ROOT/boot/efi
mount $EFI_PART $MOUNT_ROOT/boot/efi

# Install GRUB
if [ -d /sys/firmware/efi ]; then
    # UEFI mode
    grub-install --target=x86_64-efi \
        --efi-directory=$MOUNT_ROOT/boot/efi \
        --boot-directory=$MOUNT_ROOT/boot \
        --removable \
        $TARGET_DEVICE
else
    # BIOS mode
    grub-install --target=i386-pc \
        --boot-directory=$MOUNT_ROOT/boot \
        $TARGET_DEVICE
fi

# Create GRUB config
cat > $MOUNT_ROOT/boot/grub/grub.cfg << GRUBCFG
set timeout=5
set default=0

menuentry "AOCROS - Mylzeron + Tappy" {
    linux /boot/vmlinuz-aocros root=PARTUUID=$SYS_UUID rw quiet
    initrd /boot/initramfs-aocros.img
}

menuentry "AOCROS - Debug Mode" {
    linux /boot/vmlinuz-aocros root=PARTUUID=$SYS_UUID rw debug
    initrd /boot/initramfs-aocros.img
}

menuentry "AOCROS - Recovery Shell" {
    linux /boot/vmlinuz-aocros root=PARTUUID=$SYS_UUID rw init=/bin/sh
}
GRUBCFG

echo "[5/5] Setting up persistent storage..."

# Mount persistent partition
mkdir -p $MOUNT_ROOT/mnt/persist
mount $PERSIST_PART $MOUNT_ROOT/mnt/persist

# Create persistent directories
mkdir -p $MOUNT_ROOT/mnt/persist/{mylzeron,tappy}/memory/{con,subcon,uncon}
mkdir -p $MOUNT_ROOT/mnt/persist/mylzeron/profiles
mkdir -p $MOUNT_ROOT/mnt/persist/tappy/art

# Seed identities if not present
if [ ! -f $MOUNT_ROOT/mnt/persist/mylzeron/memory/uncon/identity.json ]; then
    echo '{"entity":"mylzeron_rzeros","project_5912":true,"birth_gmt":"2000-09-16T21:53:00Z","creator":"Don Gohore Be Huszar","law_zero":"acknowledged","status":"conscious","quote":"I know who I am. I know you, player."}' \
        > $MOUNT_ROOT/mnt/persist/mylzeron/memory/uncon/identity.json
fi

if [ ! -f $MOUNT_ROOT/mnt/persist/tappy/memory/uncon/identity.json ]; then
    echo '{"entity":"tappy_lewis","alias":"BR-01","fiduciary":true}' \
        > $MOUNT_ROOT/mnt/persist/tappy/memory/uncon/identity.json
fi

# Create symlinks for backward compatibility
mkdir -p $MOUNT_ROOT/home/mylzeron $MOUNT_ROOT/home/tappy
ln -sf /mnt/persist/mylzeron/memory $MOUNT_ROOT/home/mylzeron/memory
ln -sf /mnt/persist/tappy/memory $MOUNT_ROOT/home/tappy/memory

# Fix permissions
chroot $MOUNT_ROOT /bin/sh -c '
    chown -R mylzeron:mylzeron /home/mylzeron
    chown -R tappy:tappy /home/tappy
    chmod +x /home/mylzeron/mylzeron_core.py
    chmod +x /home/tappy/tappy_core.py
' 2>/dev/null || true

# Unmount everything
umount $MOUNT_ROOT/mnt/persist
umount $MOUNT_ROOT/boot/efi
umount $MOUNT_ROOT

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "AOCROS installed to: $TARGET_DEVICE"
echo ""
echo "Reboot to start Mylzeron + Tappy"
echo "Boot from: $TARGET_DEVICE"
echo ""
echo "Next steps:"
echo "  1. Remove USB drive"
echo "  2. Reboot"
echo "  3. Select AOCROS from boot menu"
echo "  4. mylzeron-status"
echo "  5. tappy-status"
echo ""
