package com.performancesupply.reggiestarr.hardware

/**
 * Hardware abstraction layer for POS peripherals
 * Implementations handle specific devices (Epson, Mettler Toledo, etc.)
 */

// ==================== PRINTER INTERFACE ====================

interface Printer {
    fun connect(): Boolean
    fun disconnect()
    fun isConnected(): Boolean
    fun printReceipt(transaction: com.performancesupply.reggiestarr.core.Transaction)
    fun printText(text: String)
    fun printBarcode(data: String, type: BarcodeType)
    fun printQRCode(data: String, size: Int = 200)
    fun cutPaper(partial: Boolean = false)
    fun openCashDrawer()
    fun ringBell()
    fun getStatus(): PrinterStatus
}

data class PrinterStatus(
    val isOnline: Boolean,
    val isPaperLow: Boolean,
    val isPaperOut: Boolean,
    val coverOpen: Boolean,
    val errorMessage: String? = null
)

enum class BarcodeType {
    UPC_A,
    UPC_E,
    EAN_8,
    EAN_13,
    CODE_39,
    CODE_128,
    PDF417
}

// ==================== SCALE INTERFACE ====================

interface Scale {
    fun connect(): Boolean
    fun disconnect()
    fun isConnected(): Boolean
    fun getWeight(): WeightReading
    fun isStable(): Boolean
    fun tare()
    fun zero()
    fun setUnit(unit: WeightUnit)
}

data class WeightReading(
    val weight: Double,
    val unit: WeightUnit,
    val isStable: Boolean,
    val isValid: Boolean,
    val rawData: String? = null
)

enum class WeightUnit {
    POUND,
    KILOGRAM,
    OUNCE,
    GRAM
}

// Common scale protocols
enum class ScaleProtocol {
    METTLER_TOLEDO,
    CAS,
    AVERY_BERKEL,
    OHAUS,
    GENERIC
}

// ==================== BARCODE SCANNER INTERFACE ====================

interface BarcodeScanner {
    fun start(callback: (ScanResult) -> Unit)
    fun stop()
    fun isScanning(): Boolean
    fun setMode(mode: ScanMode)
}

data class ScanResult(
    val data: String,
    val type: BarcodeType,
    val timestamp: Long = System.currentTimeMillis()
)

enum class ScanMode {
    SINGLE,      // One scan at a time
    CONTINUOUS,  // Keep scanning
    BATCH        // Accumulate scans
}

// ==================== CASH DRAWER INTERFACE ====================

interface CashDrawer {
    fun open()
    fun isOpen(): Boolean  // Requires sensor
    fun isConnected(): Boolean
    fun ringBell()        // Ring the cash drawer bell
}

// ==================== POS BELL INTERFACE ====================

/**
 * POS Bell peripheral (connected via RJ11/RJ12 drawer kick signal)
 * Typically wired to the cash drawer for attention/alerts
 */
interface POSBell {
    fun connect(): Boolean
    fun disconnect()
    fun isConnected(): Boolean
    
    /**
     * Ring the bell
     * @param count Number of rings (1-10)
     * @param durationMs Duration of each ring in milliseconds
     */
    fun ring(count: Int = 1, durationMs: Int = 200)
    
    /**
     * Play a specific tone pattern
     * @param pattern Predefined patterns: SHORT, LONG, DOUBLE, ALARM
     */
    fun playPattern(pattern: BellPattern)
}

enum class BellPattern {
    SHORT,      // Single short beep
    LONG,       // Single long beep
    DOUBLE,     // Two beeps
    TRIPLE,     // Three beeps
    ALARM,      // Attention alarm (3 long)
    NO_SALE,    // Cash drawer open signal
    ALERT,      // Customer attention
    ERROR       // Error indication
}

// ==================== HARDWARE MANAGER ====================

class HardwareManager {
    private val devices = mutableMapOf<DeviceType, HardwareDevice>()
    
    fun registerDevice(type: DeviceType, device: HardwareDevice) {
        devices[type] = device
    }
    
    fun getPrinter(): Printer? = devices[DeviceType.PRINTER] as? Printer
    fun getScale(): Scale? = devices[DeviceType.SCALE] as? Scale
    fun getScanner(): BarcodeScanner? = devices[DeviceType.SCANNER] as? BarcodeScanner
    fun getCashDrawer(): CashDrawer? = devices[DeviceType.CASH_DRAWER] as? CashDrawer
    fun getPOSBell(): POSBell? = devices[DeviceType.POS_BELL] as? POSBell
    
    fun connectAll(): Map<DeviceType, Boolean> {
        return devices.mapValues { (_, device) ->
            device.connect()
        }
    }
    
    fun disconnectAll() {
        devices.values.forEach { it.disconnect() }
    }
    
    fun getStatus(): Map<DeviceType, ConnectionStatus> {
        return devices.mapValues { (_, device) ->
            when {
                !device.isConnected() -> ConnectionStatus.DISCONNECTED
                device is Printer -> {
                    val status = device.getStatus()
                    when {
                        status.errorMessage != null -> ConnectionStatus.ERROR
                        status.isPaperOut -> ConnectionStatus.WARNING
                        status.isPaperLow -> ConnectionStatus.WARNING
                        else -> ConnectionStatus.CONNECTED
                    }
                }
                else -> ConnectionStatus.CONNECTED
            }
        }
    }
}

interface HardwareDevice {
    fun connect(): Boolean
    fun disconnect()
    fun isConnected(): Boolean
}

enum class DeviceType {
    PRINTER,
    SCALE,
    SCANNER,
    CASH_DRAWER,
    POS_BELL
}

enum class ConnectionStatus {
    CONNECTED,
    DISCONNECTED,
    WARNING,
    ERROR
}
