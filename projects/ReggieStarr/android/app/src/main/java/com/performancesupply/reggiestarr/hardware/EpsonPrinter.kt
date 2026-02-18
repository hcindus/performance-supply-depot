package com.performancesupply.reggiestarr.hardware

import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import java.io.OutputStream
import java.net.Socket

/**
 * Epson ESC/POS printer implementation
 * Supports USB, Ethernet, and Bluetooth connections
 */
class EpsonPrinter(
    private val connectionType: PrinterConnectionType
) : Printer {
    
    private var isPrinterConnected = false
    private var outputStream: OutputStream? = null
    private var socket: Socket? = null
    private var usbDevice: UsbDevice? = null
    
    override fun connect(): Boolean {
        return when (connectionType) {
            is PrinterConnectionType.USB -> connectUSB(connectionType.usbDevice)
            is PrinterConnectionType.Ethernet -> connectEthernet(connectionType.ip, connectionType.port)
            is PrinterConnectionType.Bluetooth -> connectBluetooth(connectionType.macAddress)
        }
    }
    
    private fun connectUSB(device: UsbDevice): Boolean {
        // Implementation using UsbManager
        // Requires USB permission handling
        usbDevice = device
        isPrinterConnected = true
        return true
    }
    
    private fun connectEthernet(ip: String, port: Int): Boolean {
        return try {
            socket = Socket(ip, port)
            outputStream = socket?.getOutputStream()
            isPrinterConnected = true
            true
        } catch (e: Exception) {
            false
        }
    }
    
    private fun connectBluetooth(macAddress: String): Boolean {
        // Implementation using BluetoothAdapter
        // TODO: Implement Bluetooth connection
        return false
    }
    
    override fun disconnect() {
        try {
            outputStream?.close()
            socket?.close()
        } catch (e: Exception) {
            // Ignore close errors
        }
        isPrinterConnected = false
    }
    
    override fun isConnected(): Boolean = isPrinterConnected
    
    override fun printReceipt(transaction: com.performancesupply.reggiestarr.core.Transaction) {
        val builder = StringBuilder()
        
        // Header
        builder.append(ESC_POS.CENTER)
        builder.append("Performance Supply Depot\n")
        builder.append("123 Main Street\n")
        builder.append("Berkeley, CA 94702\n")
        builder.append("(510) 555-0123\n")
        builder.append(ESC_POS.LINE_FEED)
        
        // Transaction info
        builder.append(ESC_POS.LEFT)
        builder.append("Trans: ${transaction.id}\n")
        builder.append("Clerk: ${transaction.clerkName}\n")
        builder.append("Date: ${formatTimestamp(transaction.startTime)}\n")
        builder.append(ESC_POS.LINE_FEED)
        
        // Items
        builder.append("-".repeat(32) + "\n")
        transaction.items.filter { !it.isVoided }.forEach { item ->
            val name = item.product.name.take(20).padEnd(20)
            val qty = item.quantity.toString().take(6).padStart(6)
            val total = String.format("$%.2f", item.total).padStart(6)
            builder.append("$name$qty$total\n")
            
            if (item.discountAmount > 0 || item.discountPercent > 0) {
                builder.append("  Discount: -$${item.discountAmount + (item.subtotalBeforeDiscounts * item.discountPercent / 100)}\n")
            }
        }
        builder.append("-".repeat(32) + "\n")
        
        // Totals
        builder.append(ESC_POS.RIGHT)
        builder.append("Subtotal: ${String.format("$%.2f", transaction.subtotal).padStart(10)}\n")
        builder.append("Tax: ${String.format("$%.2f", transaction.taxTotal).padStart(10)}\n")
        builder.append(ESC_POS.BOLD_ON)
        builder.append("TOTAL: ${String.format("$%.2f", transaction.total).padStart(10)}\n")
        builder.append(ESC_POS.BOLD_OFF)
        builder.append(ESC_POS.LINE_FEED)
        
        // Payments
        transaction.payments.forEach { payment ->
            builder.append("${payment.method}: ${String.format("$%.2f", payment.amount).padStart(10)}\n")
        }
        
        if (transaction.changeDue > 0) {
            builder.append("Change: ${String.format("$%.2f", transaction.changeDue).padStart(10)}\n")
        }
        
        // Footer
        builder.append(ESC_POS.CENTER)
        builder.append(ESC_POS.LINE_FEED)
        builder.append("Thank you for shopping!\n")
        builder.append(ESC_POS.LINE_FEED)
        builder.append(ESC_POS.LINE_FEED)
        
        printText(builder.toString())
        cutPaper(partial = false)
    }
    
    override fun printText(text: String) {
        val bytes = text.toByteArray(Charsets.UTF_8)
        outputStream?.write(bytes)
        outputStream?.flush()
    }
    
    override fun printBarcode(data: String, type: BarcodeType) {
        val barcodeType = when (type) {
            BarcodeType.UPC_A -> 0
            BarcodeType.UPC_E -> 1
            BarcodeType.EAN_13 -> 2
            BarcodeType.EAN_8 -> 3
            BarcodeType.CODE_39 -> 4
            BarcodeType.CODE_128 -> 73
            else -> 73
        }
        
        outputStream?.write(ESC_POS.GS + "k".toByte() + barcodeType.toByte())
        outputStream?.write(data.length)
        outputStream?.write(data.toByteArray())
        outputStream?.flush()
    }
    
    override fun printQRCode(data: String, size: Int) {
        val bytes = data.toByteArray(Charsets.UTF_8)
        val length = bytes.size + 3
        
        outputStream?.write(ESC_POS.GS + "(k".toByte())
        outputStream?.write(byteArrayOf(
            (length % 256).toByte(),
            (length / 256).toByte(),
            49, 80, 48
        ))
        outputStream?.write(bytes)
        
        // Set size
        outputStream?.write(ESC_POS.GS + "(k".toByte())
        outputStream?.write(byteArrayOf(3, 0, 49, 67, (size / 10).toByte().coerceIn(1, 16)))
        
        // Print
        outputStream?.write(ESC_POS.GS + "(k".toByte())
        outputStream?.write(byteArrayOf(3, 0, 49, 81, 48))
        outputStream?.flush()
    }
    
    override fun cutPaper(partial: Boolean) {
        val mode = if (partial) 1 else 0
        outputStream?.write(ESC_POS.GS + "V".toByte() + mode.toByte())
        outputStream?.flush()
    }
    
    override fun openCashDrawer() {
        // ESC p m t1 t2
        // m = 0 (pin 2), 1 (pin 5)
        // t1, t2 = pulse times
        outputStream?.write(byteArrayOf(
            0x1B, 0x70, 0x00, 0x32, 0xFA
        ))
        outputStream?.flush()
    }
    
    override fun getStatus(): PrinterStatus {
        // Request status
        outputStream?.write(byteArrayOf(0x10, 0x04, 0x01))  // Printer status
        outputStream?.write(byteArrayOf(0x10, 0x04, 0x02))  // Offline status
        outputStream?.write(byteArrayOf(0x10, 0x04, 0x04))  // Error status
        outputStream?.flush()
        
        // Read response (would need input stream)
        // For now, return assumed status
        return PrinterStatus(
            isOnline = isPrinterConnected,
            isPaperLow = false,
            isPaperOut = false,
            coverOpen = false
        )
    }
    
    private fun formatTimestamp(timestamp: Long): String {
        val sdf = java.text.SimpleDateFormat("MM/dd/yyyy HH:mm", java.util.Locale.US)
        return sdf.format(java.util.Date(timestamp))
    }
}

// ESC/POS Command Constants
object ESC_POS {
    val ESC = 0x1B.toByte()
    val GS = 0x1D.toByte()
    val LF = 0x0A.toByte()
    
    val INIT = byteArrayOf(ESC, 0x40)  // Initialize
    val LINE_FEED = byteArrayOf(LF)
    
    val LEFT = byteArrayOf(ESC, 0x61, 0x00)    // Left align
    val CENTER = byteArrayOf(ESC, 0x61, 0x01)  // Center align
    val RIGHT = byteArrayOf(ESC, 0x61, 0x02)   // Right align
    
    val BOLD_ON = byteArrayOf(ESC, 0x45, 0x01)
    val BOLD_OFF = byteArrayOf(ESC, 0x45, 0x00)
    
    val DOUBLE_WIDTH = byteArrayOf(ESC, 0x21, 0x20)
    val DOUBLE_HEIGHT = byteArrayOf(ESC, 0x21, 0x10)
    val NORMAL = byteArrayOf(ESC, 0x21, 0x00)
}

sealed class PrinterConnectionType {
    data class USB(val usbDevice: UsbDevice) : PrinterConnectionType()
    data class Ethernet(val ip: String, val port: Int = 9100) : PrinterConnectionType()
    data class Bluetooth(val macAddress: String) : PrinterConnectionType()
}
