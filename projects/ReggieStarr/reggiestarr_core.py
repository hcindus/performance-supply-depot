#!/usr/bin/env python3
"""
ReggieStarr Core - Enhanced POS System
Complete implementation with all features for testing

This version includes:
- All tax types (standard, non-tax, exempt, inclusive)
- Discounts (flat and percentage)
- Payment processing
- Inventory tracking
- Receipt generation
- Reporting
"""

import sqlite3
import datetime
import uuid
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json

# ============================================================================
# ENUMS
# ============================================================================

class TaxType(Enum):
    STANDARD = "standard"      # Add tax to price
    NON_TAX = "non_tax"        # No tax applied
    EXEMPT = "exempt"          # No tax, tracked separately
    INCLUSIVE = "inclusive"    # Tax included in price

class TransactionStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    VOIDED = "voided"
    HOLD = "hold"

class PaymentMethod(Enum):
    CASH = "Cash"
    CREDIT = "Credit"
    DEBIT = "Debit"
    EBT = "EBT"
    WIC = "WIC"
    CHECK = "Check"
    GIFT_CARD = "Gift Card"
    STORE_CREDIT = "Store Credit"

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Product:
    """A product in the inventory"""
    plu_code: str
    name: str
    price: float
    department: str = "General"
    tax_rates: List[str] = field(default_factory=list)
    quantity: int = 0
    track_inventory: bool = False
    
    def __post_init__(self):
        if self.tax_rates is None:
            self.tax_rates = []

@dataclass
class TransactionItem:
    """A line item in a transaction"""
    id: str
    plu_code: str
    name: str
    quantity: float
    unit_price: float
    tax_amount: float = 0.0
    total: float = 0.0
    discount_amount: float = 0.0
    discount_percent: float = 0.0
    tax_type: TaxType = TaxType.STANDARD
    is_voided: bool = False
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal after discounts"""
        base = self.unit_price * self.quantity
        flat_discount = self.discount_amount
        pct_discount = base * (self.discount_percent / 100)
        return base - flat_discount - pct_discount
    
    @property
    def subtotal_before_discounts(self) -> float:
        """Calculate subtotal before discounts"""
        return self.unit_price * self.quantity

@dataclass
class Payment:
    """A payment on a transaction"""
    method: str
    amount: float
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    reference: Optional[str] = None

@dataclass
class Transaction:
    """A sales transaction"""
    id: str
    clerk_name: str
    start_time: datetime.datetime
    items: List[TransactionItem] = field(default_factory=list)
    payments: List[Payment] = field(default_factory=list)
    subtotal: float = 0.0
    tax_total: float = 0.0
    total: float = 0.0
    status: TransactionStatus = TransactionStatus.ACTIVE
    change: float = 0.0
    
    def __post_init__(self):
        if isinstance(self.start_time, str):
            self.start_time = datetime.datetime.fromisoformat(self.start_time)
    
    @property
    def total_paid(self) -> float:
        return sum(p.amount for p in self.payments)
    
    @property
    def is_paid(self) -> bool:
        return self.total_paid >= self.total
    
    @property
    def change_due(self) -> float:
        return max(0, self.total_paid - self.total)
    
    @property
    def remaining_balance(self) -> float:
        return max(0, self.total - self.total_paid)

# ============================================================================
# CORE REGISTER CLASS
# ============================================================================

class CashRegister:
    """Main cash register logic"""
    
    # Tax rates (TEC MA-79 style)
    TAX_RATES = {
        'Standard': 0.0875,
        'Berkeley': 0.1025,
        'Vape': 0.125,
    }
    
    def __init__(self, db_path: str = "reggiestarr.db"):
        """Initialize the cash register with database connection"""
        self.db_path = db_path
        self.current_transaction: Optional[Transaction] = None
        self.current_clerk: Optional[str] = None
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                plu_code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                department TEXT DEFAULT 'General',
                tax_rates TEXT DEFAULT '[]',
                quantity INTEGER DEFAULT 0,
                track_inventory INTEGER DEFAULT 0
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                clerk_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                items TEXT NOT NULL,
                payments TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax_total REAL NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'completed',
                change_amount REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # CLERK OPERATIONS
    # ========================================================================
    
    def login(self, clerk_name: str) -> bool:
        """Log in a clerk"""
        self.current_clerk = clerk_name
        return True
    
    def logout(self) -> bool:
        """Log out current clerk"""
        self.current_clerk = None
        self.current_transaction = None
        return True
    
    # ========================================================================
    # PRODUCT OPERATIONS
    # ========================================================================
    
    def add_product(self, product: Product) -> bool:
        """Add or update a product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (product.plu_code, product.name, product.price, 
              product.department, json.dumps(product.tax_rates), 
              product.quantity, int(product.track_inventory)))
        conn.commit()
        conn.close()
        return True
    
    def get_product(self, plu_code: str) -> Optional[Product]:
        """Get a product by PLU code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE plu_code = ?', (plu_code,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Product(
                plu_code=row[0],
                name=row[1],
                price=row[2],
                department=row[3],
                tax_rates=json.loads(row[4]),
                quantity=row[5],
                track_inventory=bool(row[6])
            )
        return None
    
    def update_product_quantity(self, plu_code: str, delta: int):
        """Update product quantity (positive or negative)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products SET quantity = quantity + ? WHERE plu_code = ?
        ''', (delta, plu_code))
        conn.commit()
        conn.close()
    
    # ========================================================================
    # TRANSACTION OPERATIONS
    # ========================================================================
    
    def start_transaction(self) -> Transaction:
        """Start a new transaction"""
        if not self.current_clerk:
            raise RuntimeError("No clerk logged in")
        
        self.current_transaction = Transaction(
            id=str(uuid.uuid4())[:8].upper(),
            clerk_name=self.current_clerk,
            start_time=datetime.datetime.now()
        )
        return self.current_transaction
    
    def get_current_transaction(self) -> Optional[Transaction]:
        """Get the current active transaction"""
        return self.current_transaction
    
    def add_item(self, plu_code: str, quantity: float = 1.0, 
                 tax_type: TaxType = TaxType.STANDARD,
                 discount_amount: float = 0.0,
                 discount_percent: float = 0.0) -> Tuple[bool, str]:
        """Add an item to the current transaction"""
        if not self.current_transaction:
            self.start_transaction()
        
        product = self.get_product(plu_code)
        if not product:
            return False, f"Product {plu_code} not found"
        
        # Check inventory if tracking enabled
        if product.track_inventory and product.quantity < quantity:
            return False, f"Insufficient stock. Available: {product.quantity}"
        
        # Calculate item totals
        base_price = product.price * quantity
        
        # Apply discounts
        flat_discount = discount_amount
        pct_discount = base_price * (discount_percent / 100)
        discounted_price = base_price - flat_discount - pct_discount
        
        # Calculate tax based on tax type
        tax_amount = self._calculate_tax(discounted_price, product.tax_rates, tax_type)
        
        # Calculate total based on tax type
        if tax_type == TaxType.INCLUSIVE:
            total = discounted_price  # Tax already included
        else:
            total = discounted_price + tax_amount
        
        item = TransactionItem(
            id=str(uuid.uuid4())[:8].upper(),
            plu_code=plu_code,
            name=product.name,
            quantity=quantity,
            unit_price=product.price,
            tax_amount=tax_amount,
            total=total,
            discount_amount=discount_amount,
            discount_percent=discount_percent,
            tax_type=tax_type
        )
        
        self.current_transaction.items.append(item)
        
        # Update inventory if tracking
        if product.track_inventory:
            self.update_product_quantity(plu_code, -int(quantity))
        
        self._recalculate_totals()
        
        return True, f"Added {product.name} x{quantity}"
    
    def _calculate_tax(self, amount: float, tax_rates: List[str], tax_type: TaxType) -> float:
        """Calculate tax for an amount based on tax type"""
        if tax_type in (TaxType.NON_TAX, TaxType.EXEMPT):
            return 0.0
        
        total_rate = sum(self.TAX_RATES.get(rate, 0.0) for rate in tax_rates)
        
        if tax_type == TaxType.INCLUSIVE:
            # Tax is included in the price, extract it
            # amount = base + tax = base + (base * rate) = base * (1 + rate)
            # base = amount / (1 + rate)
            # tax = amount - base
            base = amount / (1 + total_rate)
            return amount - base
        else:  # STANDARD
            return amount * total_rate
    
    def _recalculate_totals(self):
        """Recalculate transaction totals"""
        if not self.current_transaction:
            return
        
        items = [item for item in self.current_transaction.items if not item.is_voided]
        
        subtotal = sum(item.subtotal for item in items)
        tax = sum(item.tax_amount for item in items)
        total = sum(item.total for item in items)
        
        self.current_transaction.subtotal = subtotal
        self.current_transaction.tax_total = tax
        self.current_transaction.total = total
    
    def void_item(self, item_id: str) -> bool:
        """Void a line item by ID"""
        if not self.current_transaction:
            return False
        
        for i, item in enumerate(self.current_transaction.items):
            if item.id == item_id:
                # Restore inventory if tracking
                product = self.get_product(item.plu_code)
                if product and product.track_inventory:
                    self.update_product_quantity(item.plu_code, int(item.quantity))
                
                # Create new voided item
                voided_item = TransactionItem(
                    id=item.id,
                    plu_code=item.plu_code,
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_amount=item.tax_amount,
                    total=item.total,
                    discount_amount=item.discount_amount,
                    discount_percent=item.discount_percent,
                    tax_type=item.tax_type,
                    is_voided=True
                )
                self.current_transaction.items[i] = voided_item
                
                self._recalculate_totals()
                return True
        
        return False
    
    def void_transaction(self) -> bool:
        """Void the entire current transaction"""
        if not self.current_transaction:
            return False
        
        # Restore all inventory
        for item in self.current_transaction.items:
            if not item.is_voided:
                product = self.get_product(item.plu_code)
                if product and product.track_inventory:
                    self.update_product_quantity(item.plu_code, int(item.quantity))
        
        self.current_transaction.status = TransactionStatus.VOIDED
        self.current_transaction = None
        return True
    
    def hold_transaction(self) -> Optional[str]:
        """Hold current transaction for later recall"""
        if not self.current_transaction:
            return None
        
        self.current_transaction.status = TransactionStatus.HOLD
        self._save_transaction(self.current_transaction)
        hold_id = self.current_transaction.id
        self.current_transaction = None
        return hold_id
    
    def recall_transaction(self, hold_id: str) -> Optional[Transaction]:
        """Recall a held transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE id = ? AND status = ?', 
                      (hold_id, 'hold'))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Load transaction
        txn = Transaction(
            id=row[0],
            clerk_name=row[1],
            start_time=datetime.datetime.fromisoformat(row[2]),
            items=[TransactionItem(**item) for item in json.loads(row[4])],
            payments=[Payment(**p) for p in json.loads(row[5])],
            subtotal=row[6],
            tax_total=row[7],
            total=row[8],
            status=TransactionStatus.ACTIVE
        )
        
        self.current_transaction = txn
        return txn
    
    # ========================================================================
    # PAYMENT OPERATIONS
    # ========================================================================
    
    def add_payment(self, method: str, amount: float, reference: str = None) -> Payment:
        """Add a payment to the transaction"""
        if not self.current_transaction:
            raise RuntimeError("No active transaction")
        
        if amount < 0:
            raise ValueError("Payment amount cannot be negative")
        
        payment = Payment(
            method=method,
            amount=amount,
            reference=reference
        )
        
        self.current_transaction.payments.append(payment)
        
        # Auto-complete if fully paid
        if self.current_transaction.is_paid:
            self._complete_transaction()
        
        return payment
    
    def _complete_transaction(self):
        """Finalize the transaction"""
        if not self.current_transaction:
            return
        
        self.current_transaction.status = TransactionStatus.COMPLETED
        self.current_transaction.change = self.current_transaction.change_due
        
        self._save_transaction(self.current_transaction)
    
    def _save_transaction(self, transaction: Transaction):
        """Save transaction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert items to dicts with serializable tax_type
        items_data = []
        for item in transaction.items:
            item_dict = asdict(item)
            item_dict['tax_type'] = item.tax_type.value if isinstance(item.tax_type, TaxType) else item.tax_type
            items_data.append(item_dict)
        
        cursor.execute('''
            INSERT OR REPLACE INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.id,
            transaction.clerk_name,
            transaction.start_time.isoformat(),
            datetime.datetime.now().isoformat() if transaction.status == TransactionStatus.COMPLETED else None,
            json.dumps(items_data),
            json.dumps([{'method': p.method, 'amount': p.amount, 
                        'timestamp': p.timestamp.isoformat(), 'reference': p.reference} 
                       for p in transaction.payments]),
            transaction.subtotal,
            transaction.tax_total,
            transaction.total,
            transaction.status.value,
            transaction.change
        ))
        conn.commit()
        conn.close()
    
    # ========================================================================
    # RECEIPT GENERATION
    # ========================================================================
    
    def generate_receipt(self) -> str:
        """Generate a text receipt for the current transaction"""
        if not self.current_transaction:
            return "No active transaction"
        
        lines = [
            "=" * 40,
            "         REGGIESTARR POS",
            "    Performance Supply Depot",
            "=" * 40,
            f"Transaction: {self.current_transaction.id}",
            f"Clerk: {self.current_transaction.clerk_name}",
            f"Date: {self.current_transaction.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 40,
        ]
        
        for item in self.current_transaction.items:
            if not item.is_voided:
                name = item.name[:20].ljust(20)
                qty = f"{item.quantity:>6.1f}"
                total = f"${item.total:>8.2f}"
                lines.append(f"{name}{qty}{total}")
                
                if item.discount_amount > 0 or item.discount_percent > 0:
                    disc_total = item.discount_amount + (item.subtotal_before_discounts * item.discount_percent / 100)
                    lines.append(f"  Discount: -${disc_total:.2f}")
        
        lines.extend([
            "-" * 40,
            f"{'Subtotal:':>30} ${self.current_transaction.subtotal:>8.2f}",
            f"{'Tax:':>30} ${self.current_transaction.tax_total:>8.2f}",
            "-" * 40,
            f"{'TOTAL:':>30} ${self.current_transaction.total:>8.2f}",
            "-" * 40,
        ])
        
        for payment in self.current_transaction.payments:
            lines.append(f"{payment.method:>20} ${payment.amount:>8.2f}")
        
        if self.current_transaction.change_due > 0:
            lines.append(f"{'Change:':>30} ${self.current_transaction.change_due:>8.2f}")
        
        lines.extend([
            "=" * 40,
            "      Thank you for shopping!",
            "=" * 40,
        ])
        
        return "\n".join(lines)
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_sales_report(self, start_date: datetime.datetime, 
                              end_date: datetime.datetime) -> str:
        """Generate a sales report for a date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE start_time BETWEEN ? AND ? AND status = 'completed'
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        total_sales = sum(row[8] for row in rows)  # total column
        total_tax = sum(row[7] for row in rows)    # tax_total column
        
        lines = [
            "SALES REPORT",
            f"Period: {start_date.date()} to {end_date.date()}",
            f"Transactions: {len(rows)}",
            f"Total Sales: ${total_sales:.2f}",
            f"Total Tax: ${total_tax:.2f}",
        ]
        
        return "\n".join(lines)
    
    def generate_z_report(self) -> str:
        """Generate Z-report (End of Day)"""
        # Get today's transactions
        now = datetime.datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE start_time >= ? AND status = 'completed'
        ''', (start_of_day.isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        total_sales = sum(row[8] for row in rows)
        total_tax = sum(row[7] for row in rows)
        transaction_count = len(rows)
        
        # Calculate payment breakdown
        payment_totals = {}
        for row in rows:
            payments = json.loads(row[5])
            for p in payments:
                method = p['method']
                payment_totals[method] = payment_totals.get(method, 0) + p['amount']
        
        lines = [
            "=" * 40,
            "           Z-REPORT",
            "         END OF DAY",
            "=" * 40,
            f"Date: {now.strftime('%Y-%m-%d')}",
            f"Time: {now.strftime('%H:%M:%S')}",
            "",
            f"Transaction Count: {transaction_count}",
            f"Total Sales: ${total_sales:.2f}",
            f"Total Tax: ${total_tax:.2f}",
            "",
            "Payment Breakdown:",
            "-" * 40,
        ]
        
        for method, amount in sorted(payment_totals.items()):
            lines.append(f"  {method:15s} ${amount:10.2f}")
        
        lines.extend([
            "-" * 40,
            f"  {'TOTAL:':15s} ${total_sales:10.2f}",
            "=" * 40,
        ])
        
        return "\n".join(lines)


# ============================================================================
# SIMPLE CLI INTERFACE
# ============================================================================

def run_cli():
    """Simple command-line interface for testing"""
    register = CashRegister()
    
    # Add sample products
    register.add_product(Product("1001", "Apple", 0.50, "Produce", ["Standard"], 100, True))
    register.add_product(Product("1002", "Sandwich", 5.99, "Food", ["Berkeley"], 50, True))
    register.add_product(Product("1003", "Vape Pen", 19.99, "Tobacco", ["Berkeley", "Vape"], 25, True))
    register.add_product(Product("1004", "Wholesale Box", 50.00, "Wholesale", [], 10, True))
    
    print("ReggieStarr Core - Test Interface")
    print("Commands: login, add, pay, receipt, report, zreport, quit")
    
    while True:
        cmd = input("\n> ").strip().lower()
        
        if cmd == "quit":
            break
        elif cmd.startswith("login "):
            register.login(cmd[6:])
            print(f"Logged in as {cmd[6:]}")
        elif cmd == "add":
            plu = input("PLU Code: ")
            qty = float(input("Quantity: "))
            print("Tax types: 1=Standard, 2=Non-Tax, 3=Exempt, 4=Inclusive")
            tax_choice = input("Tax type (1-4): ")
            tax_type = {
                '1': TaxType.STANDARD,
                '2': TaxType.NON_TAX,
                '3': TaxType.EXEMPT,
                '4': TaxType.INCLUSIVE
            }.get(tax_choice, TaxType.STANDARD)
            
            success, msg = register.add_item(plu, qty, tax_type)
            print(msg)
            if success:
                txn = register.get_current_transaction()
                print(f"Subtotal: ${txn.subtotal:.2f}, Tax: ${txn.tax_total:.2f}, Total: ${txn.total:.2f}")
        elif cmd == "pay":
            method = input("Payment Method: ")
            amount = float(input("Amount: "))
            try:
                payment = register.add_payment(method, amount)
                txn = register.get_current_transaction()
                print(f"Payment accepted. Remaining: ${txn.remaining_balance:.2f}")
                if txn.is_paid:
                    print(f"Change due: ${txn.change_due:.2f}")
            except Exception as e:
                print(f"Error: {e}")
        elif cmd == "receipt":
            print(register.generate_receipt())
        elif cmd == "report":
            end = datetime.datetime.now()
            start = end - datetime.timedelta(days=1)
            print(register.generate_sales_report(start, end))
        elif cmd == "zreport":
            print(register.generate_z_report())
        else:
            print("Unknown command")


if __name__ == "__main__":
    run_cli()
