---
name: wallet-payment-display
version: 1.0.0
description: Simple direct wallet payment display for DroidScript apps. Show BTC wallet QR codes, payment URIs, and basic verification without API integration.
author: Performance Supply Depot LLC
---

# Wallet Payment Display Skill

Zero-API crypto payment solution for DroidScript games.

## Use Case

When you want to accept crypto payments without:
- Payment processor APIs
- Complex integrations
- Transaction fees

Just display your wallet address and let users pay directly.

## Quick Start

```javascript
// Load library
var WalletPaymentDisplay = require("./lib/WalletPaymentDisplay.js");

// Initialize with your wallet
var wallet = new WalletPaymentDisplay({
    walletAddress: "bc1q...your...address",
    suggestedAmount: 0.001, // BTC
    label: "Chronospace Explorer Purchase"
});

// Show on game exit
wallet.showExitPaymentScreen({
    message: "Enjoyed the game? Support development!",
    onDismiss: function() {
        app.Exit(); // Actually exit after
    }
});
```

## Features

- QR code generation (Google Charts API)
- BIP21 payment URI support
- Multiple suggested amounts
- One-tap wallet app opening
- Address copying
- Manual transaction verification

## API Reference

### Constructor

```javascript
new WalletPaymentDisplay(config)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| walletAddress | string | required | Your BTC receiving address |
| suggestedAmount | number | 0.001 | Default payment amount |
| label | string | "" | Payment description |

### Methods

#### showExitPaymentScreen(options)

Display payment dialog.

| Option | Type | Description |
|--------|------|-------------|
| amount | number | Override default amount |
| message | string | Custom message |
| onDismiss | function | Callback on close |

#### generatePaymentURI(amount, label)

Generate BIP21 Bitcoin URI.

```javascript
var uri = wallet.generatePaymentURI(0.001, "Game Purchase");
// bitcoin:bc1q...?amount=0.001&label=Game%20Purchase
```

#### verifyPayment(txid, callback)

Verify transaction on blockchain.

```javascript
wallet.verifyPayment("txid-here", function(verified, confirmations) {
    if (verified) {
        app.ShowPopup("Confirmed! " + confirmations + " confirmations");
    }
});
```

#### checkBalance(callback)

Check wallet balance.

```javascript
wallet.checkBalance(function(balance, error) {
    if (!error) {
        app.ShowPopup("Wallet balance: " + balance + " BTC");
    }
});
```

## Security Considerations

- **Public addresses only** — Never expose private keys
- **Manual verification** — Check payments manually or via block explorer
- **No automatic unlock** — Don't auto-unlock features; verify first
- **Address reuse** — Consider generating new addresses per user

## Workflow

```
User clicks "Buy Full Version"
    ↓
Show wallet payment screen with QR
    ↓
User scans QR or copies address
    ↓
User sends payment from wallet
    ↓
User provides TXID or you check balance
    ↓
Verify on blockchain
    ↓
Unlock full game
```

## File Location

```
games/ChronospaceExplorer/lib/WalletPaymentDisplay.js
```

## Limitations

- No automatic payment detection
- Manual verification required
- No refund mechanism
- User must provide TXID or you poll balance

## When to Use

✅ Simple donation/payment flow  
✅ Low transaction volume  
✅ Trust-based verification  
✅ No API complexity wanted  

❌ High-volume sales  
❌ Automatic fulfillment required  
❌ Need instant confirmation  

## Examples

See `examples/wallet-payment-demo.js` for implementation.
