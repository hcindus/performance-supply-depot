# ReggieStarr RS-79 User Manual
## Version 1.0.0.3

---

## Overview

ReggieStarr RS-79 is a versatile Point of Sale (POS) system designed for modern retail and hospitality environments. It supports multi-language interfaces, multiple currencies (including cryptocurrencies), barcode scanning, scale integration, thermal and impact printer support (Epson TM-T88 and TM-U220B), Kitchen Display System (KDS), and cash drawer operations.

---

## System Requirements

### Hardware
- PC with COM ports (for scale/printers)
- Network access (for TM-T88 printer)
- Optional: Barcode scanner, scale, receipt printer, kitchen printer

### Software
- Python 3.x
- Required libraries:
  - `tkinter` (UI)
  - `babel` (currency formatting)
  - `requests` (API calls)
  - `qrcode` (crypto payments)
  - `pillow` (image handling)
  - `firebase-admin` (cloud sync)
  - `pynput` (keyboard input)
  - `pyserial` (hardware communication)

### Configuration
Update these settings in the code:
- Firebase credentials
- UPCItemDB API key
- Printer IP/serial ports

---

## Getting Started

1. **Launch**: Run `reggie_starr.py`
   - A splash screen welcomes you in multiple languages

2. **Enter**: Click "Enter" to access the main interface
   - Fullscreen by default (press F11 to toggle)

3. **Exit**: Close the window to see a goodbye splash
   - Click "Exit" to shut down

---

## Main Interface

### Top Row Controls

| Control | Function |
|---------|----------|
| **Language** | Select from English, Spanish, etc. |
| **Currency** | Choose USD, EUR, GBP, BTC, USDC, or USDT |
| **Update Rates** | Refresh exchange rates from API |
| **Hand Mode** | "Right Hand" (inputs left, buttons right) or "Left Hand" (vice versa) |
| **Palette** | "Bob Ross" (light theme) or "Militant" (dark theme) |
| **Print Receipts** | Enable/disable TM-T88 printing |
| **Use KDS** | Send orders to Kitchen Display System |
| **Reprint Receipt** | Reprint a past transaction's receipt |

---

## Clerk Management

| Control | Function |
|---------|----------|
| **Clerk Dropdown** | Select existing clerk or "New Clerk" |
| **Login** | Log in selected clerk |
| **Logout** | Log out current clerk |

**To add a new clerk:**
1. Select "New Clerk" from dropdown
2. Enter name
3. Click "Login"

---

## Product Entry

| Field | Description |
|-------|-------------|
| **Product Code** | Enter or scan barcode |
| **Product Name** | Auto-filled after scanning (read-only) |
| **Quantity** | Manual entry or use "Qty Pad" keypad. Scale weighs items if connected |
| **Price** | Manual entry or "Price Pad". Auto-filled from inventory |
| **Discount (%)** | Apply percentage discount |
| **Surcharge ($)** | Add flat surcharge |
| **Tax Rates** | Enter rates separated by commas (e.g., "SalesTax,LocalTax") |
| **Add Product** | Add item to transaction |

---

## Transaction Controls

| Button | Function |
|--------|----------|
| **Payment Method** | Choose Cash, BTC, MC/Visa, etc. |
| **Refund** | Process a refund |
| **Void** | Void the last transaction |
| **Exchange** | Record an exchange |
| **Cancel Transaction** | Cancel current transaction |
| **Split Check** | Split by number or items |
| **Split Tender** | Split payment across methods |
| **Hold** | Hold transaction for later |
| **Recall** | Recall a held transaction |
| **Convert Currency** | Convert last transaction amount |
| **QR Code** | Generate QR for crypto payments |
| **Scale** | Weigh item if scale connected |
| **Tare** | Set/apply tare weight |

---

## Reports and Rewards

| Button | Function |
|--------|----------|
| **Generate Report** | Financial report with tax details |
| **Group Report** | Sales by group |
| **PLU Report** | Sales by product code |
| **Period Report** | Hourly sales breakdown |
| **Sales Totals** | Sales over various periods |
| **Crypto Tax Report** | Tax report for BTC/USDC/USDT |
| **Reward Customer** | Issue BTC reward to customer |
| **AI Pricing** | Suggest prices based on demand |
| **Multi-Store Analytics** | Analyze sales across stores |

---

## Inventory Management

| Field/Button | Function |
|--------------|----------|
| **Item Name/Code** | Add or edit items |
| **Quantity/Cost/Price** | Set stock levels and pricing |
| **Alert Level** | Low stock warning threshold |
| **Desc 2** | Second description for kitchen tickets |
| **Tax Inclusive** | Check if price includes tax |
| **Add Item** | Add new item to inventory |
| **Update Stock** | Adjust stock levels |
| **Inventory Report** | View inventory status |

---

## Customer Management

| Field/Button | Function |
|--------------|----------|
| **Customer ID/Name** | Add customers |
| **Add Customer** | Save new customer |
| **View Transactions** | See customer purchase history |

---

## Key Features

### 1. Split Check

**By Number:**
1. Enter number of splits (e.g., 3)
2. System splits total evenly
3. Each split generates separate receipt

**By Item:**
1. Select items from recent transactions
2. Assign items to different splits
3. Each split gets its own receipt

**Example:**
- Add Beer ($7, tax incl.) and Burger ($12)
- Click "Split Check" → "By Item"
- Set 2 splits
- Assign Beer to Split 1, Burger to Split 2
- Result: Two receipts ($7 and $12)

### 2. Tax Inclusive Pricing

1. Check "Tax Incl" when adding item
2. Enter price with tax included (e.g., $7 Beer)
3. System backs out tax ($7 with 9% tax = $6.42 + $0.58 tax)
4. Receipt shows both amounts

### 3. Receipt Reprint

1. Click "Reprint Receipt"
2. Enter transaction number (0 = latest)
3. Receipt prints with "REPRINT" at top

### 4. Printer Configuration

**TM-T88 (Receipt Printer):**
- Default: 192.168.1.100:9100
- Prints customer receipts
- Opens cash drawer for "Cash" payments

**TM-U220B (Kitchen Printer):**
- Default: COM4
- Prints kitchen tickets
- Uses "Desc 2" field

### 5. Kitchen Display System (KDS)

1. Check "Use KDS" to enable
2. Orders logged to screen instead of printing
3. Kitchen staff mark orders complete

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Printer Not Connected** | Check IP/serial settings. TM-T88: 192.168.1.100:9100, TM-U220B: COM4 |
| **Scale Error** | Ensure COM3 is correct and scale is powered on |
| **Split by Item Fails** | Add multiple items first. Feature assumes consecutive purchases |
| **Currency Not Updating** | Check internet connection and API keys |
| **Firebase Sync Failed** | Verify Firebase credentials in configuration |

---

## Important Notes

- Replace placeholder paths/keys before production use
- Test with mock hardware if real devices aren't available
- Backup database regularly
- Train clerks on void procedures
- Set appropriate permission levels

---

## Keyboard Shortcuts

| Key | Function |
|-----|----------|
| F11 | Toggle fullscreen |
| F1 | Help |
| F2 | Clerk login |
| F3 | Clerk logout |
| F4 | Hold transaction |
| F5 | Recall transaction |
| F8 | Generate report |
| F9 | Void last item |
| F12 | Cancel transaction |

---

## Support

For technical support or feature requests, contact:
**Performance Supply Depot LLC**

---

*Manual Version: 1.0.0.3*
*Last Updated: February 18, 2026*
