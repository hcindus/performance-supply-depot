#!/bin/bash
# Quick email test using local postfix
echo "Testing email server..."

# Test 1: Check postfix is running
if systemctl is-active --quiet postfix; then
    echo "✅ Postfix is running"
else
    echo "❌ Postfix not running"
    exit 1
fi

# Test 2: Send test email
echo "Email test from Mortimer at $(date)" | \
    mail -s "Test $(date +%s)" -a "From: mortimer@myl0nr0s.cloud" \
    mortimer@myl0nr0s.cloud && \
    echo "✅ Test email queued" || \
    echo "❌ Failed to send"

# Test 3: Show mail queue
echo ""
echo "Mail queue:"
mailq | head -5 || echo "  (empty)"

# Test 4: Recent logs
echo ""
echo "Recent mail logs:"
tail -3 /var/log/mail.log 2>/dev/null || echo "  No logs yet"
