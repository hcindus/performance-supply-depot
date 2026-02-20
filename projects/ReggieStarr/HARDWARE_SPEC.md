# ReggieStarr Hardware POS Specification
## Version 5.0 - Professional Retail System

---

## Target Platforms (Priority Order)

1. **Android (Primary)** - Tablets, dedicated POS terminals
2. **Windows** - Desktop/laptop fallback
3. **Linux** - Embedded systems, Raspberry Pi
4. **iOS** - Future consideration

---

## Core Tax Requirements

### Tax Types Required
| Type | Description | Example |
|------|-------------|---------|
| **Standard Tax** | Normal sales tax | 8.75% Berkeley |
| **Non-Tax** | No tax applied | Wholesale, resale |
| **Tax Exempt** | Customer exempt | Non-profit, gov |
| **Tax Inclusive** | Tax built into price | EU VAT style |
| **Multiple Rates** | Different items, different taxes | Food 5%, Vape 12.5% |

### Tax Calculation Logic
```
Standard:     price + (price * tax_rate)
Non-Tax:      price (no tax)
Tax Exempt:   price (no tax, tracked separately)
Tax Inclusive: price (tax already included, show breakdown)
```

---

## Hardware Interface Requirements

### 1. Cash Drawer
**Interface:** RJ12/RJ11 (standard receipt printer connection)
**Trigger:** ESC/POS command via printer
**Status:** Open/closed detection (optional)
**Libraries:**
- Android: `escpos-coffee-android`, custom USB serial
- Windows: `System.IO.Ports`, `RawPrinterHelper`
- Linux: `libusb`, `pyserial`

**Open Drawer Command:**
```
ESC p m t1 t2
Where: m = 0 (pin 2), 1 (pin 5)
       t1, t2 = pulse time (default: 50, 250ms)
```

### 2. Barcode Scanner (Multi-line/2D)
**Interface Modes:**
- **USB-HID (Keyboard Emulation)** - Simplest, works everywhere
- **USB-COM (Serial)** - Direct control, status feedback
- **Bluetooth** - Wireless convenience

**Supported Formats:**
- 1D: UPC-A, UPC-E, EAN-8, EAN-13, Code 39, Code 128
- 2D: QR Code, Data Matrix, PDF417

**Multi-line Support:**
- Batch mode: Scan multiple items, then transmit
- Continuous mode: Each scan = immediate add
- Quantity prefix: Scan quantity barcode, then item

**Android Implementation:**
```java
// USB-HID mode - just listen to input field
// USB-COM mode - use UsbSerial library
UsbManager usbManager = (UsbManager) getSystemService(Context.USB_SERVICE);
UsbSerialDriver driver = UsbSerialProber.getDefaultProber().probeDevice(device);
```

### 3. Epson Thermal Printer
**Models:** TM-T88V, TM-T20, TM-m30
**Interface:** USB, Ethernet, Bluetooth
**Protocol:** ESC/POS

**Required Features:**
- Text printing (normal, double-wide, double-high)
- Barcode printing (UPC, Code 128, QR)
- Image/logo printing
- Cut command (partial/full)
- Status feedback (paper low, cover open)
- Cash drawer kick

**ESC/POS Command Reference:**
```
Initialize:        ESC @
Cut paper:         GS V m (m=0 partial, 1 full)
Feed lines:        ESC d n
Bold:              ESC E n (n=0 off, 1 on)
Align center:      ESC a 1
Barcode:           GS k m n [data]
QR Code:           GS ( k pL pH cn fn n [data]
```

**Android Printing:**
- USB: `android.hardware.usb` + custom ESC/POS builder
- Ethernet: `java.net.Socket`
- Bluetooth: `android.bluetooth`

**Cross-Platform Library Options:**
- Java: `escpos-coffee`
- C#: `ESCPOS_NET`
- C++: `libescpos` (custom)
- Python: `python-escpos`

### 4. NTEP Scale Interface
**NTEP:** National Type Evaluation Program (certified for trade)
**Interface:** RS-232 serial
**Protocol:** Common formats

**Supported Protocols:**
1. **Mettler Toledo** - Continuous or demand mode
2. **CAS** - Simple ASCII format
3. **Avery Berkel** - Demand mode
4. **Generic** - Configurable format

**Serial Settings:**
- Baud: 9600 (common), 4800, 2400
- Data: 8 bits
- Parity: None
- Stop: 1 bit

**Mettler Toledo Format:**
```
Response: "ST,GS,   1.23,kg\r\n"
          ST = Stable
          GS = Gross
          1.23 = Weight
          kg = Unit
```

**CAS Format:**
```
Response: "W,+001234\r\n"
          W = Weight
          + = Positive
          001234 = 12.34 (with decimal point implied)
```

**Android Serial:**
```java
// USB-to-Serial adapter (FTDI, Prolific, CH340)
UsbSerialDriver driver = UsbSerialProber.getDefaultProber().probeDevice(device);
UsbSerialPort port = driver.getPorts().get(0);
port.open(connection);
port.setParameters(9600, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE);

// Read weight
byte[] buffer = new byte[64];
int numBytesRead = port.read(buffer, 1000);
```

**Weight Integration Flow:**
1. Clerk presses "Weigh" button
2. System requests weight from scale
3. Scale returns stable reading
4. Price = weight × unit price
5. Add to transaction

---

## Software Architecture for Android

### Recommended Stack
```
Language: Kotlin (preferred) or Java
UI: Jetpack Compose (modern) or XML layouts
Database: Room (SQLite abstraction)
Networking: Retrofit/OkHttp
Hardware: Custom USB/Bluetooth managers
```

### Alternative: Flutter
```
Language: Dart
UI: Flutter widgets
Database: sqflite
Hardware: Platform channels to native code
Pros: Cross-platform, fast UI
Cons: Hardware access requires native code anyway
```

### Alternative: React Native
```
Language: JavaScript/TypeScript
UI: React Native components
Database: react-native-sqlite-storage
Hardware: Native modules required
```

### Recommended: Native Kotlin
Best hardware access, best performance, Android-native.

---

## Core Classes (Android/Kotlin)

```kotlin
// Transaction Management
data class Transaction(
    val id: String,
    val clerkId: String,
    val items: MutableList<LineItem>,
    var status: TransactionStatus,
    val timestamp: Long
)

data class LineItem(
    val product: Product,
    val quantity: Double,
    val weight: Double?,  // For scale items
    val unitPrice: Double,
    val taxRate: Double,
    val discount: Double,
    val taxType: TaxType  // STANDARD, NON_TAX, EXEMPT, INCLUSIVE
)

enum class TaxType {
    STANDARD,      // Add tax to price
    NON_TAX,       // No tax
    EXEMPT,        // No tax, track separately
    INCLUSIVE      // Tax included in displayed price
}

// Hardware Interfaces
interface Printer {
    fun printReceipt(transaction: Transaction)
    fun printReport(report: Report)
    fun openDrawer()
    fun getStatus(): PrinterStatus
}

interface Scale {
    fun connect(): Boolean
    fun getWeight(): WeightReading
    fun isStable(): Boolean
}

data class WeightReading(
    val weight: Double,
    val unit: String,
    val stable: Boolean
)

interface BarcodeScanner {
    fun startListening(callback: (String) -> Unit)
    fun stopListening()
}

interface CashDrawer {
    fun open()
    fun isOpen(): Boolean  // If sensor available
}
```

---

## Database Schema (Room)

```kotlin
@Entity
data class ProductEntity(
    @PrimaryKey val plu: String,
    val name: String,
    val price: Double,
    val unit: String,  // EACH, LB, KG, OZ
    val departmentId: String,
    val taxRates: String,  // JSON array
    val isWeighed: Boolean,  // Requires scale
    val barcode: String?
)

@Entity
data class TransactionEntity(
    @PrimaryKey val id: String,
    val clerkId: String,
    val startTime: Long,
    val endTime: Long?,
    val subtotal: Double,
    val taxTotal: Double,
    val total: Double,
    val status: String
)

@Entity
data class LineItemEntity(
    @PrimaryKey val id: String,
    val transactionId: String,
    val productPlu: String,
    val quantity: Double,
    val weight: Double?,
    val unitPrice: Double,
    val taxAmount: Double,
    val total: Double
)
```

---

## UI Screens

### 1. Main POS Screen
```
+--------------------------------------------------+
|  [Logo]  Transaction #1234    Clerk: John  [Menu]|
+--------------------------------------------------+
|                                                  |
|  +--------------------------------------------+  |
|  | Item          Qty    Price    Total        |  |
|  | Apple         2      $0.50   $1.00         |  |
|  | Banana (WT)   1.2lb  $1.99   $2.39         |  |
|  |                                              |  |
|  | SUBTOTAL:                    $3.39         |  |
|  | TAX (8.75%):                 $0.30         |  |
|  | TOTAL:                       $3.69         |  |
|  +--------------------------------------------+  |
|                                                  |
|  [1] [2] [3]  [PLU]  [Weigh]  [Discount]       |
|  [4] [5] [6]  [Qty]  [Void]   [Tax Exempt]     |
|  [7] [8] [9]  [Dept] [Hold]   [Note]           |
|  [.] [0] [C]  [Search]         [Pay]           |
|                                                  |
+--------------------------------------------------+
```

### 2. Payment Screen
```
+--------------------------------------------------+
|  TOTAL: $3.69                                    |
|                                                  |
|  [Cash]    [Credit]    [Debit]                   |
|  [EBT]     [WIC]       [Check]                   |
|  [Gift Card]  [Store Credit]                     |
|                                                  |
|  Amount Tendered: $5.00                          |
|  Change Due: $1.31                               |
|                                                  |
|  [Print Receipt]  [Email Receipt]  [No Receipt]  |
|                                                  |
+--------------------------------------------------+
```

### 3. Hardware Status Screen
```
+--------------------------------------------------+
|  HARDWARE STATUS                                 |
|                                                  |
|  Printer:     [Connected] TM-T88V                |
|  Drawer:      [Closed]                           |
|  Scanner:     [Active] USB-HID                   |
|  Scale:       [Connected] 0.00 lb (Stable)       |
|                                                  |
|  [Test Print]  [Open Drawer]  [Test Scale]       |
|                                                  |
+--------------------------------------------------+
```

---

## Implementation Phases

### Phase 1: Core POS (MVP)
- Basic transaction flow
- Product database
- Simple tax calculation
- Cash payment only
- Basic receipt (text/log)

### Phase 2: Hardware Integration
- Epson printer support
- Cash drawer control
- Barcode scanner (USB-HID)

### Phase 3: Advanced Features
- Scale integration
- Multiple payment types
- Discounts and promotions
- Tax inclusive/exempt

### Phase 4: Polish
- Touchscreen optimization
- Offline mode
- Cloud sync
- Reporting

---

## Recommended Development Approach

1. **Start with Android native Kotlin**
2. **Use Jetpack Compose** for UI
3. **Implement hardware in phases:**
   - Printer first (most critical)
   - Scanner second (productivity)
   - Scale third (specialized)
   - Drawer last (simple)
4. **Test on real hardware early**

---

## Hardware Testing Checklist

- [ ] Printer prints text
- [ ] Printer cuts paper
- [ ] Printer opens drawer
- [ ] Printer reports status
- [ ] Scanner reads 1D barcodes
- [ ] Scanner reads QR codes
- [ ] Scale returns weight
- [ ] Scale stability detection
- [ ] Drawer opens on command
- [ ] All work simultaneously

---

## Next Steps

1. **Confirm Android as primary platform**
2. **Choose development approach** (Native Kotlin vs Flutter)
3. **Acquire test hardware** (printer, scanner, scale)
4. **Start Phase 1 implementation**

---

*Specification Version: 5.0*
*Date: February 18, 2026*
