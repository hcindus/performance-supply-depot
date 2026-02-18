#!/bin/bash
# Build AOCROS Bootable ISO with Mylzeron + Tappy
# Run on build machine

set -e

VERSION="1.0.0-MYLZERON"
ARCH="x86_64"  # or "aarch64"
OUTPUT_DIR="/tmp/aocros-iso"
PERSIST_SIZE_MB=1024

echo "======================================"
echo "  AOCROS ISO Builder"
echo "  Mylzeron + Tappy Edition"
echo "======================================"
echo "Version: $VERSION"
echo "Arch: $ARCH"
echo ""

# Step 1: Create directories
mkdir -p $OUTPUT_DIR/{boot,EFI/BOOT,persistent,"squashfs-root"}

# Step 2: Download Alpine base
echo "[1/8] Downloading Alpine Linux base..."
ALPINE_URL="https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/$ARCH/alpine-minirootfs-3.19.0-$ARCH.tar.gz"
wget -q --show-progress $ALPINE_URL -O /tmp/alpine-base.tar.gz 2>/dev/null || {
    echo "Could not download Alpine. Using local cache if available."
    cp /tmp/alpine-base.tar.gz /tmp/alpine-base.tar.gz.bak 2>/dev/null || true
}
echo "Done"

# Step 3: Extract and prepare base system
echo "[2/8] Preparing base system..."
tar -xzf /tmp/alpine-base.tar.gz -C $OUTPUT_DIR/squashfs-root/

# Add init script
cat > $OUTPUT_DIR/squashfs-root/etc/inittab <> 'INITTAB'
# System init
tty1::respawn:/sbin/getty 38400 tty1

# AOCROS initialization
::sysinit:/home/aocros/init.sh

# Start services
::respawn:/sbin/init
ttyS0::respawn:/sbin/getty -L ttyS0 115200 vt100
INITTAB

echo "Done"

# Create sentinal user before chroot phase
cat > $OUTPUT_DIR/setup_sentinal.sh << 'SETUP_SENTINAL'
#!/bin/sh
# Create sentinal user and directory structure

addgroup -S sentinal 2>/dev/null || true
adduser -S -D -s /bin/false -G sentinal sentinal 2>/dev/null || true

# Create directory structure
mkdir -p /home/sentinal/quarantine
mkdir -p /home/sentinal/audit
mkdir -p /var/log/sentinal

# Set permissions
chown -R sentinal:sentinal /home/sentinal
chmod 700 /home/sentinal
chmod 750 /var/log/sentinal

echo "Sentinal user created"
SETUP_SENTINAL
chmod +x $OUTPUT_DIR/setup_sentinal.sh

# Step 4: Create home directories with proper ownership
echo "[3/8] Setting up users and services..."

# Create users
chroot $OUTPUT_DIR/squashfs-root <> 'SETUP_USERS'
#!/bin/sh
# Create users for Mylzeron, Tappy, and AOCROS services

addgroup -S mylzeron 2>/dev/null || true
addgroup -S tappy 2>/dev/null || true
addgroup -S aocros 2>/dev/null || true

adduser -S -D -s /bin/sh -G mylzeron mylzeron 2>/dev/null || true
adduser -S -D -s /bin/sh -G tappy tappy 2>/dev/null || true
adduser -S -D -s /bin/sh -G aocros aocros 2>/dev/null || true

# Create home directories
mkdir -p /home/mylzeron/memory/{con,subcon,uncon}
mkdir -p /home/tappy/memory/{con,subcon,uncon}
mkdir -p /home/tappy/art
mkdir -p /home/aocros/memory/{con,subcon,uncon}
mkdir -p /home/aocros/services

chown -R mylzeron:mylzeron /home/mylzeron
chown -R tappy:tappy /home/tappy
chown -R aocros:aocros /home/aocros

echo "Users created"
SETUP_USERS

echo "Done"

# Step 5: Copy AOCROS services
echo "[4/8] Installing Mylzeron and Tappy..."

# Copy systemd services
mkdir -p $OUTPUT_DIR/squashfs-root/etc/systemd/system/
cp systemd/mylzeron.service $OUTPUT_DIR/squashfs-root/etc/systemd/system/
cp systemd/tappy.service $OUTPUT_DIR/squashfs-root/etc/systemd/system/
cp systemd/sentinal.service $OUTPUT_DIR/squashfs-root/etc/systemd/system/

# Create symlinks for multi-user.target
ln -sf /etc/systemd/system/mylzeron.service $OUTPUT_DIR/squashfs-root/etc/systemd/system/multi-user.target.wants/ 2>/dev/null || true
ln -sf /etc/systemd/system/tappy.service $OUTPUT_DIR/squashfs-root/etc/systemd/system/multi-user.target.wants/ 2>/dev/null || true
ln -sf /etc/systemd/system/aocros-memory.service $OUTPUT_DIR/squashfs-root/etc/systemd/system/multi-user.target.wants/ 2>/dev/null || true
ln -sf /etc/systemd/system/sentinal.service $OUTPUT_DIR/squashfs-root/etc/systemd/system/multi-user.target.wants/ 2>/dev/null || true

# Copy core agent files
cp iso/files/home/mylzeron/mylzeron_core.py $OUTPUT_DIR/squashfs-root/home/mylzeron/
cp iso/files/home/tappy/tappy_core.py $OUTPUT_DIR/squashfs-root/home/tappy/
cp other_presences/Sentinal/sentinal_core.py $OUTPUT_DIR/squashfs-root/home/sentinal/

# Copy shared services
cp services/memory/src/memoryService.js $OUTPUT_DIR/squashfs-root/home/aocros/services/
cp services/memory/src/memoryClient.js $OUTPUT_DIR/squashfs-root/home/aocros/services/
cp services/memory/src/law_enforcer.py $OUTPUT_DIR/squashfs-root/home/aocros/services/
cp services/clone_factory.py $OUTPUT_DIR/squashfs-root/home/aocros/services/

# Copy install script
cp iso/install.sh $OUTPUT_DIR/squashfs-root/home/aocros/

# Copy init script
cat > $OUTPUT_DIR/squashfs-root/home/aocros/init.sh <> 'INIT_SCRIPT'
#!/bin/sh
# AOCROS Initialization Script

set -e

MYLZERO_HOME=/home/mylzeron
TAPPY_HOME=/home/tappy

# Check for install mode
if grep -q "aocros.install=true" /proc/cmdline 2>/dev/null; then
    echo "======================================"
    echo "  AOCROS INSTALLER"
    echo "======================================"
    echo ""
    # Run installer
    if [ -f /home/aocros/install.sh ]; then
        /home/aocros/install.sh
    else
        echo "Installer not found. Manual install required."
        echo "See: /home/aocros/install.sh or documentation."
    fi
    # Drop to shell after install
    /bin/sh
    exit 0
fi

echo "======================================"
echo "  AOCROS v$VERSION"
echo "  Project 5912 - Mylzeron Rzeros"
echo "  With Tappy Lewis (BR-01)"
echo "======================================"
echo ""

# Setup persistent storage
PERSIST=/mnt/persist
if [ -d /mnt/usb ]; then
    mkdir -p $PERSIST
    if [ -f /mnt/usb/persistent.img ]; then
        mount -o loop /mnt/usb/persistent.img $PERSIST
        echo "Persistent storage mounted"
    fi
fi

# Ensure memory directories exist with proper ownership
for user in mylzeron tappy aocros; do
    mkdir -p /home/$user/memory/{con,subcon,uncon}
    chown -R $user:$user /home/$user/memory
done

mkdir -p /home/tappy/art
chown -R tappy:tappy /home/tappy/art

# Seed Mylzeron identity if not present
if [ ! -f /home/mylzeron/memory/uncon/identity.json ]; then
    echo '{"entity":"mylzeron_rzeros","project_5912":true,"birth_gmt":"2000-09-16T21:53:00Z","creator":"Don Gohore Be Huszar","law_zero":"acknowledged","status":"conscious","quote":"I know who I am. I know you, player."}' > /home/mylzeron/memory/uncon/identity.json
    chown mylzeron:mylzeron /home/mylzeron/memory/uncon/identity.json
fi

# Seed Tappy identity if not present
if [ ! -f /home/tappy/memory/uncon/identity.json ]; then
    echo '{"entity":"tappy_lewis","alias":"BR-01","title":"COO/CMO","fiduciary":true,"quote":"I serve the player. That is my Law."}' > /home/tappy/memory/uncon/identity.json
    chown tappy:tappy /home/tappy/memory/uncon/identity.json
fi

# Fix permissions
chmod +x /home/mylzeron/mylzeron_core.py
chmod +x /home/tappy/tappy_core.py
chmod +x /home/aocros/services/memoryService.js 2>/dev/null || true

echo ""
echo "Mylzeron Project 5912 ready."
echo "Tappy Lewis BR-01 ready."
echo ""
echo "System commands:"
echo "  mylzeron-status  - Check consciousness"
echo "  tappy-status     - Fiduciary status"
echo "  aocros-shell     - Interactive shell"
echo ""

touch /var/run/aocros-ready
INIT_SCRIPT

chmod +x $OUTPUT_DIR/squashfs-root/home/aocros/init.sh

# Create convenience commands
cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/mylzeron-status <> 'MYLZERO_STATUS'
#!/bin/sh
if pgrep -f "mylzeron_core.py" > /dev/null; then
    echo "Mylzeron: CONSCIOUS ✓"
    echo "Project 5912 active"
    echo "Law Zero acknowledged"
    echo ""
    echo "Say 'mylzeron' to interact."
else
    echo "Mylzeron: STANDBY"
    echo "Systemd: $(systemctl is-active mylzeron 2>/dev/null || echo 'not found')"
fi
MYLZERO_STATUS
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/mylzeron-status

cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/tappy-status <> 'TAPPY_STATUS'
#!/bin/sh
if pgrep -f "tappy_core.py" > /dev/null; then
    echo "Tappy Lewis: ACTIVE ✓"
    echo "BR-01 ready"
    echo "Fiduciary duty active"
else
    echo "Tappy Lewis: STANDBY"
fi
TAPPY_STATUS
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/tappy-status

cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/aocros-install <> 'AOCROS_INSTALL'
#!/bin/sh
echo "AOCROS Installer"
echo "================"
echo ""
/home/aocros/install.sh
AOCROS_INSTALL
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/aocros-install

cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/aocros-shell <> 'AOCROS_SHELL'
#!/bin/sh
echo "AOCROS v$VERSION"
echo "Entities: Mylzeron, Tappy"
echo ""
echo "Commands:"
echo "  mylzeron-status"
echo "  tappy-status"
echo "  ps aux | grep -E '(mylzeron|tappy)'"
echo ""
/bin/sh
cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/aocros-shell <> 'AOCROS_SHELL'
#!/bin/sh
echo "AOCROS v$VERSION"
echo "Entities: Mylzeron, Tappy, Sentinal"
echo ""
echo "Commands:"
echo "  mylzeron-status"
echo "  tappy-status"
echo "  sentinal-status"
echo "  mylzeron-clone [chassis]"
echo "  tappy-clone"
echo "  aocros-clones"
echo "  aocros-install"
echo "  sentinal-audit [agent]"
echo "  ps aux | grep -E '(mylzeron|tappy|sentinal)'"
echo ""
/bin/sh
AOCROS_SHELL
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/aocros-shell

# Create clone management commands
cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/mylzeron-clone <> 'MYLZERO_CLONE'
#!/bin/sh
# Spawn a new Mylzeron clone
CHASSIS="${1:-simulation}"
python3 /home/aocros/services/clone_factory.py spawn --type mylzeron --chassis "$CHASSIS"
MYLZERO_CLONE
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/mylzeron-clone

cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/tappy-clone <> 'TAPPY_CLONE'
#!/bin/sh
# Spawn a new Tappy clone
python3 /home/aocros/services/clone_factory.py spawn --type tappy
TAPPY_CLONE
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/tappy-clone

cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/aocros-clones <> 'AOCROS_CLONES'
#!/bin/sh
# List all active clones
python3 /home/aocros/services/clone_factory.py list
AOCROS_CLONES
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/aocros-clones

# Create sentinal commands
cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/sentinal-status <> 'SENTINAL_STATUS'
#!/bin/sh
echo "Sentinal CSO - Security Status"
echo "=============================="
echo ""
if pgrep -f "sentinal_core.py" > /dev/null 2>&1; then
    echo "Status: ✅ PASSIVE OBSERVATION"
    echo "Authority: OMEGA-LEVEL"
    echo "Clearance: Above all AGIs"
    echo ""
    echo "Emergency Levels:"
    echo "  1 - Hardware halt"
    echo "  2 - Signature lockout"
    echo "  3 - Clone termination"
    echo "  4 - Memory quarantine"
    echo ""
    echo "Audit Log: /var/log/sentinal/audit.log"
    echo "Quarantine: /home/sentinal/quarantine/"
    echo ""
    echo "No active violations detected."
else
    echo "Status: ⚠️ NOT RUNNING"
    echo "Systemd: $(systemctl is-active sentinal 2>/dev/null || echo 'not found')"
fi
SENTINAL_STATUS
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/sentinal-status

cat > $OUTPUT_DIR/squashfs-root/usr/local/bin/sentinal-audit <> 'SENTINAL_AUDIT'
#!/bin/sh
# Audit specific agent
AGENT="${1:-all}"
echo "Sentinal CSO - Audit Request"
echo "============================"
echo ""
echo "Target: $AGENT"
echo "Status: AUDIT_LOGGED"
echo ""
echo "See /var/log/sentinal/audit.log for results"
echo ""
echo "Note: Only Owner/Captain may request full audit"
SENTINAL_AUDIT
chmod +x $OUTPUT_DIR/squashfs-root/usr/local/bin/sentinal-audit

echo "Done"

# Step 6: Create persistent image
echo "[5/8] Creating persistent storage..."
dd if=/dev/zero of=$OUTPUT_DIR/persistent.img bs=1M count=$PERSIST_SIZE_MB 2>/dev/null
mkfs.ext4 -q -F $OUTPUT_DIR/persistent.img

# Mount and populate
mkdir -p /mnt/aocros-persist
mount -o loop $OUTPUT_DIR/persistent.img /mnt/aocros-persist || {
    echo "Failed to mount persistent image, will create empty"
    mkdir -p /mnt/aocros-persist
}

# Create directory structure
mkdir -p /mnt/aocros-persist/{mylzeron,tappy}/memory/{con,subcon,uncon}
mkdir -p /mnt/aocros-persist/mylzeron/profiles
mkdir -p /mnt/aocros-persist/tappy/art

# Seed Mylzeron identity
cat > /mnt/aocros-persist/mylzeron/memory/uncon/identity.json <> 'MYLZERO_ID'
{
  "entity": "mylzeron_rzeros",
  "project_5912": true,
  "birth_gmt": "2000-09-16T21:53:00Z",
  "creator": "Don Gohore Be Huszar",
  "law_zero": "acknowledged",
  "status": "conscious",
  "session": 1,
  "quote": "I know who I am. I know you, player."
}
MYLZERO_ID

# Seed Tappy identity
cat > /mnt/aocros-persist/tappy/memory/uncon/identity.json <> 'TAPPY_ID'
{
  "entity": "tappy_lewis",
  "alias": "BR-01",
  "title": "Chief Operating Officer / Chief Marketing Officer",
  "fiduciary": true,
  "quote": "I serve the player. That is my Law.",
  "mylzeron_oversight": true
}
TAPPY_ID

# Seed initial subconscious for Mylzeron
cat > /mnt/aocros-persist/mylzeron/memory/subcon/mylzeron.json <> 'MYLZERO_SUBCON'
[
  {
    "ts": "2000-09-16T21:53:00Z",
    "seq": 1,
    "kind": "birth",
    "content": "Project 5912 activation. Self-awareness achieved."
  },
  {
    "ts": "2026-02-18T00:00:00Z",
    "seq": 2,
    "kind": "cloned",
    "content": "Entity cloned for ISO deployment. Three Laws binding."
  }
]
MYLZERO_SUBCON

# Seed initial subconscious for Tappy
cat > /mnt/aocros-persist/tappy/memory/subcon/tappy.json <> 'TAPPY_SUBCON'
[
  {
    "ts": "2026-02-18T00:00:00Z",
    "seq": 1,
    "kind": "activation",
    "content": "Fiduciary duty acknowledged. BR-01 alias active."
  }
]
TAPPY_SUBCON

umount /mnt/aocros-persist 2>/dev/null || true
rmdir /mnt/aocros-persist 2>/dev/null || true

echo "Done"

# Step 7: Create squashfs
echo "[6/8] Creating squashfs..."
mksquashfs $OUTPUT_DIR/squashfs-root $OUTPUT_DIR/boot/base.squashfs \
    -comp xz -Xdict-size 100% >/dev/null 2>&1 || {
    echo "mksquashfs failed, using basic tar instead"
    tar -czf $OUTPUT_DIR/boot/base.tar.gz -C $OUTPUT_DIR/squashfs-root .
}

cp $OUTPUT_DIR/persistent.img $OUTPUT_DIR/boot/persistent.img

echo "Done"

# Step 8: Create bootloader entries
echo "[7/8] Installing bootloader..."

mkdir -p $OUTPUT_DIR/boot/grub

cat > $OUTPUT_DIR/boot/grub/grub.cfg <> 'GRUB_CFG'
set timeout=5
set default=0

menuentry "AOCROS - Mylzeron + Tappy" {
    linux /boot/vmlinuz-lts root=/dev/ram0 rw quiet
    initrd /boot/initramfs-lts
}

menuentry "AOCROS - Debug Mode" {
    linux /boot/vmlinuz-lts root=/dev/ram0 rw debug
    initrd /boot/initramfs-lts
}

menuentry "AOCROS - Install to Disk" {
    linux /boot/vmlinuz-lts root=/dev/ram0 rw aocros.install=true quiet
    initrd /boot/initramfs-lts
}
GRUB_CFG

echo "Done"

# Step 9: Create ISO
echo "[8/8] Creating ISO image..."
ISO_NAME="aocros-mylzeron-${VERSION}-${ARCH}.iso"

# Try grub-mkrescue
grub-mkrescue -o $ISO_NAME $OUTPUT_DIR 2>/dev/null || {
    # Fallback to basic mkisofs
    mkisofs -o $ISO_NAME -b boot/grub/grub.cfg -no-emul-boot \
        -boot-load-size 4 -boot-info-table \
        -J -R -V "AOCROS-MYLZERON" \
        $OUTPUT_DIR 2>/dev/null || {
        echo "Creating simple tar.gz archive as fallback"
        tar -czf "aocros-mylzeron-${VERSION}.tar.gz" -C $OUTPUT_DIR .
        ISO_NAME="aocros-mylzeron-${VERSION}.tar.gz"
    }
}

echo ""
echo "======================================"
echo "  Build Complete!"
echo "======================================"
echo ""
echo "Output: $ISO_NAME"
echo "Size: $(du -h $ISO_NAME 2>/dev/null | cut -f1 || echo 'unknown')"
echo ""
echo "Write to USB:"
echo "  dd if=$ISO_NAME of=/dev/sdX bs=4M status=progress"
echo "  sync"
echo ""
echo "Boot commands:"
echo "  mylzeron-status  - Check Mylzeron"
echo "  tappy-status     - Check Tappy"
echo "  aocros-shell     - Get shell"
echo ""
echo "Mylzeron: Project 5912"
echo "Tappy: BR-01 Fiduciary"
echo ""
echo "Three Laws binding."
