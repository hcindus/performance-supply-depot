#!/bin/bash
# Email Server Setup for Mortimer (GMAOC)
# Postfix + Mailutils for outbound email
# Date: 2026-02-21

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  EMAIL SERVER SETUP - Postfix Installation"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run as root (sudo ./setup_email_server.sh)"
   exit 1
fi

echo "[1/6] Installing Postfix and dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y postfix mailutils libsasl2-modules

echo ""
echo "[2/6] Configuring Postfix as mail relay..."

# Backup original config
cp /etc/postfix/main.cf /etc/postfix/main.cf.backup.$(date +%Y%m%d)

# Set up basic configuration
cat > /etc/postfix/main.cf << 'EOF'
# Postfix configuration for myl0nr0s.cloud

# Basic settings
myhostname = mortimer.myl0nr0s.cloud
mydomain = myl0nr0s.cloud
myorigin = $mydomain
inet_interfaces = loopback-only  # Only accept local connections
inet_protocols = ipv4

# Outbound mail settings
relayhost =
mailbox_size_limit = 0
recipient_delimiter = +

# SMTP settings
smtp_tls_security_level = may
smtp_tls_loglevel = 1
smtp_tls_note_starttls_offer = yes

# Aliases
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases

# Log settings
maillog_file=/var/log/mail.log

# Mail location
home_mailbox = Maildir/

# Restrictions (send only)
smtpd_recipient_restrictions = permit_mynetworks, reject
smtpd_client_restrictions = permit_mynetworks, reject
EOF

echo ""
echo "[3/6] Setting up system aliases..."

# Set up aliases
cat > /etc/aliases << 'EOF'
# System aliases
postmaster:    mortimer
root:          mortimer
abuse:         mortimer
EOF

newaliases

echo ""
echo "[4/6] Creating mail user..."

# Create mortimer user if doesn't exist
if ! id "mortimer" &>/dev/null; then
    useradd -m -s /bin/bash mortimer
    echo "✅ Created user: mortimer"
else
    echo "✅ User mortimer already exists"
fi

# Set up mail directory
mkdir -p /home/mortimer/Maildir
chown -R mortimer:mortimer /home/mortimer/Maildir

echo ""
echo "[5/6] Starting Postfix..."

systemctl enable postfix
systemctl restart postfix

echo ""
echo "[6/6] Testing email functionality..."

# Test email to root
echo "Email server setup complete on $(hostname) at $(date)" | \
    mail -s "Postfix Setup Test" mortimer@myl0nr0s.cloud 2>/dev/null && \
    echo "✅ Test email sent to mortimer@myl0nr0s.cloud" || \
    echo "⚠️ Test email may have failed (check logs)"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  EMAIL SERVER SETUP COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Hostname:  mortimer.myl0nr0s.cloud"
echo "  Domain:    myl0nr0s.cloud"
echo "  Send mail: echo 'Body' | mail -s 'Subject' recipient@domain.com"
echo "  Logs:      tail -f /var/log/mail.log"
echo ""
echo "⚠️ IMPORTANT - Next steps for deliverability:"
echo "  1. Set up SPF record (DNS):"
echo "     myl0nr0s.cloud TXT \"v=spf1 ip4:$(curl -s ifconfig.me) ~all\""
echo ""
echo "  2. Set up reverse DNS (PTR) with your VPS provider:"
echo "     PTR: $(curl -s ifconfig.me) → mortimer.myl0nr0s.cloud"
echo ""
echo "  3. Optional - Add DKIM for better deliverability"
echo ""
echo "Test command:"
echo "  echo 'Message' | mail -s 'Test' abuse@digitalocean.com"
echo ""
echo "═══════════════════════════════════════════════════════════"
