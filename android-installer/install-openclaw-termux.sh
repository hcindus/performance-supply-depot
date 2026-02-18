#!/data/data/com.termux/files/usr/bin/bash
# OpenClaw Installer for Termux
# Performance Supply Depot LLC
# Handles Android version compatibility gracefully

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 OpenClaw Setup - Starting...${NC}"
echo ""

# Check Android version
SDK=$(getprop ro.build.version.sdk 2>/dev/null || echo "0")
if [ "$SDK" -lt 26 ]; then
    echo -e "${YELLOW}⚠️  Android API $SDK detected${NC}"
    echo -e "${YELLOW}   (OpenClaw works best on Android 8+ / API 26+)${NC}"
    echo ""
    echo -e "Options for your device:${NC}"
    echo "  1. Install UserLAnd from Play Store (RECOMMENDED)"
    echo "  2. Use proot-distro for full Linux"
    echo "  3. Continue with limited Termux setup"
    echo ""
    read -p "Continue with limited setup? (y/N): " choice
    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}💡 Install UserLAnd from Play Store for best results${NC}"
        exit 0
    fi
    LIMITED_MODE=true
fi

echo -e "${BLUE}📦 Updating packages...${NC}"
pkg update -y || {
    echo -e "${YELLOW}⚠️ Update had issues, continuing...${NC}"
}

if [ "$LIMITED_MODE" = true ]; then
    echo -e "${BLUE}🔧 Installing minimal packages for old Android...${NC}"
    pkg install -y git nodejs-lts openssh
else
    echo -e "${BLUE}🔧 Installing full package set...${NC}"
    pkg install -y git nodejs openssh tmux wget curl python
fi

echo -e "${BLUE}🔐 Setting up SSH access...${NC}"
sshd 2>/dev/null || echo -e "${YELLOW}⚠️ SSH may already be running${NC}"

echo ""
echo -e "${GREEN}✅ SSH server ready!${NC}"
echo ""

# Get network info
echo -e "${BLUE}🌐 Network information:${NC}"
ifconfig 2>/dev/null | grep "inet " | head -1 || ip addr show 2>/dev/null | grep "inet " | head -1

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. ${YELLOW}Set password:${NC} passwd"
echo -e "  2. ${YELLOW}From your laptop:${NC} ssh user@PHONE_IP -p 8022"
echo -e "  3. ${YELLOW}Install OpenClaw:${NC} npm i -g openclaw"
echo -e "  4. ${YELLOW}Start OpenClaw:${NC} termux-chroot openclaw onboard"
echo ""

# Offer to install OpenClaw now
read -p "Install OpenClaw now? (Y/n): " install
if [[ ! "$install" =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}🤖 Installing OpenClaw...${NC}"
    if [ "$LIMITED_MODE" = true ]; then
        npm i -g openclaw --unsafe-perm || {
            echo -e "${RED}❌ Install failed. Try:${NC}"
            echo "npm cache clean --force"
            echo "npm i -g openclaw --unsafe-perm"
        }
    else
        npm i -g openclaw || {
            echo -e "${RED}❌ Install failed. Try with --force flag${NC}"
        }
    fi
fi

echo -e "${GREEN}🌟 All done! Welcome to OpenClaw!${NC}"
