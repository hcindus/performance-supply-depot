package com.performancesupply.reggiestarr.hardware

import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbDeviceConnection
import android.hardware.usb.UsbManager
import com.hoho.android.usbserial.driver.UsbSerialDriver
import com.hoho.android.usbserial.driver.UsbSerialPort
import com.hoho.android.usbserial.driver.UsbSerialProber
import java.nio.charset.Charset

/**
 * NTEP Scale implementation using USB-to-Serial adapter
 * Supports Mettler Toledo, CAS, Avery Berkel protocols
 */
class NTEPScale(
    private val usbManager: UsbManager,
    private val protocol: ScaleProtocol = ScaleProtocol.METTLER_TOLEDO,
    private val baudRate: Int = 9600
) : Scale {
    
    private var serialPort: UsbSerialPort? = null
    private var connection: UsbDeviceConnection? = null
    private var isScaleConnected = false
    private var currentWeight = WeightReading(0.0, WeightUnit.POUND, false, false)
    private var currentUnit = WeightUnit.POUND
    
    override fun connect(): Boolean {
        // Find USB serial device
        val availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(usbManager)
        
        if (availableDrivers.isEmpty()) {
            return false
        }
        
        val driver = availableDrivers.first()
        val device: UsbDevice = driver.device
        
        // Request permission if needed
        val permissionIntent = android.app.PendingIntent.getBroadcast(
            null, 0, android.content.Intent("com.android.example.USB_PERMISSION"), 0
        )
        
        if (!usbManager.hasPermission(device)) {
            usbManager.requestPermission(device, permissionIntent)
            return false
        }
        
        connection = usbManager.openDevice(device)
        if (connection == null) {
            return false
        }
        
        serialPort = driver.ports.firstOrNull()
        if (serialPort == null) {
            return false
        }
        
        return try {
            serialPort?.open(connection)
            serialPort?.setParameters(baudRate, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE)
            isScaleConnected = true
            startReading()
            true
        } catch (e: Exception) {
            disconnect()
            false
        }
    }
    
    private fun startReading() {
        // Start a thread to continuously read from the scale
        Thread {
            val buffer = ByteArray(64)
            
            while (isScaleConnected) {
                try {
                    val numBytes = serialPort?.read(buffer, 1000) ?: 0
                    if (numBytes > 0) {
                        val data = String(buffer, 0, numBytes, Charset.forName("US-ASCII"))
                        parseWeightData(data)
                    }
                } catch (e: Exception) {
                    // Handle read error
                }
            }
        }.start()
    }
    
    private fun parseWeightData(data: String) {
        currentWeight = when (protocol) {
            ScaleProtocol.METTLER_TOLEDO -> parseMettlerToledo(data)
            ScaleProtocol.CAS -> parseCAS(data)
            ScaleProtocol.AVERY_BERKEL -> parseAveryBerkel(data)
            ScaleProtocol.OHAUS -> parseOhaus(data)
            ScaleProtocol.GENERIC -> parseGeneric(data)
        }
    }
    
    /**
     * Mettler Toledo format: "ST,GS,   1.23,kg\r\n"
     * ST = Stable, GS = Gross
     */
    private fun parseMettlerToledo(data: String): WeightReading {
        val lines = data.split("\r\n", "\n")
        
        for (line in lines) {
            val parts = line.split(",")
            if (parts.size >= 4) {
                val stable = parts[0] == "ST" || parts[0] == "ST,"
                val weightStr = parts[2].trim()
                val unitStr = parts[3].trim()
                
                val weight = weightStr.toDoubleOrNull() ?: 0.0
                val unit = when (unitStr.lowercase()) {
                    "kg", "kilogram" -> WeightUnit.KILOGRAM
                    "lb", "lbs", "pound" -> WeightUnit.POUND
                    "oz", "ounce" -> WeightUnit.OUNCE
                    "g", "gram" -> WeightUnit.GRAM
                    else -> currentUnit
                }
                
                return WeightReading(weight, unit, stable, true, line)
            }
        }
        
        return currentWeight.copy(isValid = false)
    }
    
    /**
     * CAS format: "W,+001234\r\n" (12.34 with implied decimal)
     */
    private fun parseCAS(data: String): WeightReading {
        val lines = data.split("\r\n", "\n")
        
        for (line in lines) {
            if (line.startsWith("W,")) {
                val parts = line.split(",")
                if (parts.size >= 2) {
                    val weightStr = parts[1]
                    val sign = if (weightStr.startsWith("-")) -1 else 1
                    val weightInt = weightStr.filter { it.isDigit() }.toIntOrNull() ?: 0
                    val weight = weightInt * sign / 100.0  // Implied 2 decimal places
                    
                    return WeightReading(weight, currentUnit, true, true, line)
                }
            }
        }
        
        return currentWeight.copy(isValid = false)
    }
    
    /**
     * Avery Berkel format: Similar to Mettler Toledo
     */
    private fun parseAveryBerkel(data: String): WeightReading {
        // Similar to Mettler Toledo
        return parseMettlerToledo(data)
    }
    
    /**
     * Ohaus format: "  1.23 lb \r\n"
     */
    private fun parseOhaus(data: String): WeightReading {
        val lines = data.split("\r\n", "\n")
        
        for (line in lines) {
            val trimmed = line.trim()
            val parts = trimmed.split(" ")
            
            if (parts.size >= 2) {
                val weight = parts[0].toDoubleOrNull() ?: 0.0
                val unit = when (parts[1].lowercase()) {
                    "kg" -> WeightUnit.KILOGRAM
                    "lb", "lbs" -> WeightUnit.POUND
                    "oz" -> WeightUnit.OUNCE
                    "g" -> WeightUnit.GRAM
                    else -> currentUnit
                }
                
                return WeightReading(weight, unit, true, true, line)
            }
        }
        
        return currentWeight.copy(isValid = false)
    }
    
    private fun parseGeneric(data: String): WeightReading {
        // Try to extract any number from the data
        val regex = Regex("""(\d+\.?\d*)""")
        val match = regex.find(data)
        
        return if (match != null) {
            val weight = match.value.toDoubleOrNull() ?: 0.0
            WeightReading(weight, currentUnit, true, true, data)
        } else {
            currentWeight.copy(isValid = false)
        }
    }
    
    override fun disconnect() {
        isScaleConnected = false
        try {
            serialPort?.close()
            connection?.close()
        } catch (e: Exception) {
            // Ignore close errors
        }
        serialPort = null
        connection = null
    }
    
    override fun isConnected(): Boolean = isScaleConnected
    
    override fun getWeight(): WeightReading = currentWeight
    
    override fun isStable(): Boolean = currentWeight.isStable
    
    override fun tare() {
        // Send tare command (protocol specific)
        when (protocol) {
            ScaleProtocol.METTLER_TOLEDO -> sendCommand("T\r\n")
            ScaleProtocol.CAS -> sendCommand("T\r\n")
            else -> { /* Not supported */ }
        }
    }
    
    override fun zero() {
        // Send zero command
        when (protocol) {
            ScaleProtocol.METTLER_TOLEDO -> sendCommand("Z\r\n")
            ScaleProtocol.CAS -> sendCommand("Z\r\n")
            else -> { /* Not supported */ }
        }
    }
    
    override fun setUnit(unit: WeightUnit) {
        currentUnit = unit
        // Some scales support unit switching via command
        // Implementation depends on specific scale model
    }
    
    private fun sendCommand(command: String) {
        try {
            serialPort?.write(command.toByteArray(), 1000)
        } catch (e: Exception) {
            // Handle write error
        }
    }
}
