package com.performancesupply.reggiestarr.core

import java.util.UUID

/**
 * Core data models for ReggieStarr POS
 * These are platform-agnostic and can be shared across Android, Desktop, etc.
 */

enum class TaxType {
    STANDARD,      // Add tax to price
    NON_TAX,       // No tax applied
    EXEMPT,        // No tax, tracked separately
    INCLUSIVE      // Tax included in displayed price
}

enum class PaymentMethod {
    CASH,
    CREDIT,
    DEBIT,
    EBT,
    WIC,
    CHECK,
    GIFT_CARD,
    STORE_CREDIT
}

enum class TransactionStatus {
    ACTIVE,
    COMPLETED,
    VOIDED,
    HOLD
}

data class Product(
    val plu: String,
    val name: String,
    val price: Double,
    val unit: UnitOfMeasure = UnitOfMeasure.EACH,
    val department: String = "General",
    val taxRates: List<TaxRate> = emptyList(),
    val isWeighed: Boolean = false,
    val barcode: String? = null,
    val trackInventory: Boolean = false,
    val quantityOnHand: Int = 0
)

enum class UnitOfMeasure {
    EACH,
    POUND,
    KILOGRAM,
    OUNCE,
    GRAM
}

data class TaxRate(
    val name: String,
    val rate: Double,  // e.g., 0.0875 for 8.75%
    val isDefault: Boolean = false
)

data class LineItem(
    val id: String = UUID.randomUUID().toString().take(8).uppercase(),
    val product: Product,
    val quantity: Double,
    val weight: Double? = null,  // For scale items
    val unitPrice: Double,
    val discountAmount: Double = 0.0,
    val discountPercent: Double = 0.0,
    val taxType: TaxType = TaxType.STANDARD,
    val isVoided: Boolean = false
) {
    val subtotal: Double
        get() = unitPrice * quantity - discountAmount - (subtotalBeforeDiscounts * discountPercent / 100)
    
    val subtotalBeforeDiscounts: Double
        get() = unitPrice * quantity
    
    val taxAmount: Double
        get() = when (taxType) {
            TaxType.STANDARD -> product.taxRates.sumOf { it.rate * subtotal }
            TaxType.INCLUSIVE -> {
                val totalRate = product.taxRates.sumOf { it.rate }
                subtotal - (subtotal / (1 + totalRate))
            }()
            else -> 0.0
        }
    
    val total: Double
        get() = when (taxType) {
            TaxType.INCLUSIVE -> subtotal
            else -> subtotal + taxAmount
        }
}

data class Payment(
    val id: String = UUID.randomUUID().toString().take(8).uppercase(),
    val method: PaymentMethod,
    val amount: Double,
    val timestamp: Long = System.currentTimeMillis(),
    val reference: String? = null  // For credit card auth codes, check numbers, etc.
)

data class Transaction(
    val id: String = UUID.randomUUID().toString().take(8).uppercase(),
    val clerkId: String,
    val clerkName: String,
    val startTime: Long = System.currentTimeMillis(),
    var endTime: Long? = null,
    val items: MutableList<LineItem> = mutableListOf(),
    val payments: MutableList<Payment> = mutableListOf(),
    var status: TransactionStatus = TransactionStatus.ACTIVE
) {
    val subtotal: Double
        get() = items.filter { !it.isVoided }.sumOf { it.subtotal }
    
    val taxTotal: Double
        get() = items.filter { !it.isVoided }.sumOf { it.taxAmount }
    
    val total: Double
        get() = items.filter { !it.isVoided }.sumOf { it.total }
    
    val totalPaid: Double
        get() = payments.sumOf { it.amount }
    
    val changeDue: Double
        get() = (totalPaid - total).coerceAtLeast(0.0)
    
    val remainingBalance: Double
        get() = (total - totalPaid).coerceAtLeast(0.0)
    
    val isPaid: Boolean
        get() = remainingBalance <= 0.0
}

/**
 * Calculator for complex tax scenarios
 */
object TaxCalculator {
    
    fun calculateTax(amount: Double, taxRates: List<TaxRate>, taxType: TaxType): Double {
        return when (taxType) {
            TaxType.STANDARD -> {
                val totalRate = taxRates.sumOf { it.rate }
                amount * totalRate
            }
            TaxType.INCLUSIVE -> {
                val totalRate = taxRates.sumOf { it.rate }
                amount - (amount / (1 + totalRate))
            }
            else -> 0.0
        }
    }
    
    fun extractTaxFromInclusive(totalWithTax: Double, taxRates: List<TaxRate>): Pair<Double, Double> {
        val totalRate = taxRates.sumOf { it.rate }
        val baseAmount = totalWithTax / (1 + totalRate)
        val taxAmount = totalWithTax - baseAmount
        return Pair(baseAmount, taxAmount)
    }
}
