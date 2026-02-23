package com.performancesupply.reggiestarr.core

/**
 * Main cash register logic - business rules and transaction management
 */
class CashRegister(
    private val productRepository: ProductRepository,
    private val transactionRepository: TransactionRepository
) {
    private var currentTransaction: Transaction? = null
    private var currentClerk: Clerk? = null
    
    // Tax rates configuration
    val taxRates = mutableListOf(
        TaxRate("Standard", 0.0875, true),
        TaxRate("Berkeley", 0.1025),
        TaxRate("Vape", 0.125)
    )
    
    // ==================== @/FOR MULTIPLIER ====================
    
    /**
     * Parse @/For multiplier syntax: "6 @ $3.50" or "10 @ 5.00"
     * Returns Pair(quantity, unitPrice) or null if not multiplier syntax
     */
    fun parseMultiplierSyntax(input: String): Pair<Double, Double>? {
        val atIndex = input.indexOf('@')
        if (atIndex == -1) return null
        
        try {
            val qtyStr = input.substring(0, atIndex).trim()
            val priceStr = input.substring(atIndex + 1).trim()
                .replace("$", "")
                .replace(",", "")
            
            val quantity = qtyStr.toDouble()
            val unitPrice = priceStr.toDouble()
            
            return Pair(quantity, unitPrice)
        } catch (e: NumberFormatException) {
            return null
        }
    }
    
    // ==================== CLERK OPERATIONS ====================
    
    fun login(clerk: Clerk): Boolean {
        currentClerk = clerk
        return true
    }
    
    fun logout() {
        currentClerk = null
        currentTransaction = null
    }
    
    fun getCurrentClerk(): Clerk? = currentClerk
    
    // ==================== TRANSACTION OPERATIONS ====================
    
    fun startTransaction(): Transaction {
        val clerk = currentClerk ?: throw IllegalStateException("No clerk logged in")
        
        currentTransaction = Transaction(
            clerkId = clerk.id,
            clerkName = clerk.name
        )
        
        return currentTransaction!!
    }
    
    fun getCurrentTransaction(): Transaction? = currentTransaction
    
    fun addItem(
        plu: String,
        quantity: Double = 1.0,
        weight: Double? = null,
        taxType: TaxType = TaxType.STANDARD,
        discountAmount: Double = 0.0,
        discountPercent: Double = 0.0
    ): Result<LineItem> {
        val transaction = currentTransaction ?: startTransaction()
        
        val product = productRepository.getProduct(plu)
            ?: return Result.failure(IllegalArgumentException("Product not found: $plu"))
        
        // Use weight for weighed items, quantity otherwise
        val finalQuantity = if (product.isWeighed && weight != null) {
            weight
        } else {
            quantity
        }
        
        val lineItem = LineItem(
            product = product,
            quantity = finalQuantity,
            weight = weight,
            unitPrice = product.price,
            taxType = taxType,
            discountAmount = discountAmount,
            discountPercent = discountPercent
        )
        
        transaction.items.add(lineItem)
        
        return Result.success(lineItem)
    }
    
    /**
     * Add item using @/For multiplier syntax: "6 @ $3.50" for retail operations
     * @param input The @/For string (e.g., "6 @ 3.50")
     * @param taxType Tax type to apply
     * @param discountPercent Optional discount percentage
     * @return Result with LineItem or failure
     */
    fun addItemWithMultiplier(
        input: String,
        taxType: TaxType = TaxType.STANDARD,
        discountPercent: Double = 0.0
    ): Result<LineItem> {
        val parsed = parseMultiplierSyntax(input)
            ?: return Result.failure(IllegalArgumentException("Invalid @/For syntax: $input (expected: '6 @ 3.50')"))
        
        val transaction = currentTransaction ?: startTransaction()
        
        val (quantity, unitPrice) = parsed
        
        val lineItem = LineItem(
            product = Product(
                plu = "@MULT",
                name = "Multiplied Item",
                price = unitPrice,
                isWeighed = false
            ),
            quantity = quantity,
            weight = null,
            unitPrice = unitPrice,
            taxType = taxType,
            discountPercent = discountPercent
        )
        
        transaction.items.add(lineItem)
        
        return Result.success(lineItem)
    }
    
    fun voidItem(lineItemId: String): Boolean {
        val transaction = currentTransaction ?: return false
        
        val item = transaction.items.find { it.id == lineItemId }
            ?: return false
        
        // Mark as voided (don't remove, for audit trail)
        val index = transaction.items.indexOf(item)
        transaction.items[index] = item.copy(isVoided = true)
        
        return true
    }
    
    fun voidTransaction(): Boolean {
        val transaction = currentTransaction ?: return false
        transaction.status = TransactionStatus.VOIDED
        currentTransaction = null
        return true
    }
    
    fun holdTransaction(): String? {
        val transaction = currentTransaction ?: return null
        transaction.status = TransactionStatus.HOLD
        // Save to repository for later recall
        transactionRepository.saveTransaction(transaction)
        val holdId = transaction.id
        currentTransaction = null
        return holdId
    }
    
    fun recallTransaction(holdId: String): Transaction? {
        val transaction = transactionRepository.getTransaction(holdId)
            ?: return null
        
        if (transaction.status != TransactionStatus.HOLD) {
            return null
        }
        
        currentTransaction = transaction.copy(
            status = TransactionStatus.ACTIVE
        )
        return currentTransaction
    }
    
    // ==================== PAYMENT OPERATIONS ====================
    
    fun addPayment(method: PaymentMethod, amount: Double, reference: String? = null): Payment {
        val transaction = currentTransaction 
            ?: throw IllegalStateException("No active transaction")
        
        val payment = Payment(
            method = method,
            amount = amount,
            reference = reference
        )
        
        transaction.payments.add(payment)
        
        // Auto-complete if fully paid
        if (transaction.isPaid) {
            completeTransaction()
        }
        
        return payment
    }
    
    fun completeTransaction(): Transaction? {
        val transaction = currentTransaction ?: return null
        
        transaction.endTime = System.currentTimeMillis()
        transaction.status = TransactionStatus.COMPLETED
        
        // Save to repository
        transactionRepository.saveTransaction(transaction)
        
        // Return completed transaction and clear current
        val completed = transaction
        currentTransaction = null
        return completed
    }
    
    // ==================== UTILITY ====================
    
    fun canAddPayment(): Boolean {
        return currentTransaction?.let { it.remainingBalance > 0 } ?: false
    }
    
    fun getRemainingBalance(): Double {
        return currentTransaction?.remainingBalance ?: 0.0
    }
}

// Repository interfaces - to be implemented with Room or other storage
interface ProductRepository {
    fun getProduct(plu: String): Product?
    fun getProductByBarcode(barcode: String): Product?
    fun saveProduct(product: Product)
    fun getAllProducts(): List<Product>
}

interface TransactionRepository {
    fun saveTransaction(transaction: Transaction)
    fun getTransaction(id: String): Transaction?
    fun getTransactions(startTime: Long, endTime: Long): List<Transaction>
}

data class Clerk(
    val id: String,
    val name: String,
    val role: ClerkRole = ClerkRole.CLERK
)

enum class ClerkRole {
    ADMIN,
    MANAGER,
    CLERK
}
