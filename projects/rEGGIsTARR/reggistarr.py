#!/usr/bin/env python3
"""
rEGGIsTARR - Retail Electronic Goods & General Inventory Transaction and Receipt Recorder
Complete Point-of-Sale System for Performance Supply Depot LLC

Based on TEC MA-79 Cash Register Owner's Manual (pages 26-35)
Enhanced with modern features: BTC payments, cloud backup, advanced reporting

Author: Performance Supply Depot LLC
Version: 4.0.0
Date: February 18, 2026
"""

import datetime
import json
import sqlite3
import os
import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ==================== CONFIGURATION ====================

class Config:
    """System configuration"""
    STORE_NAME = "Performance Supply Depot"
    STORE_ADDRESS = "123 Main Street, Berkeley, CA 94702"
    STORE_PHONE = "(510) 555-0123"
    STORE_EMAIL = "support@performancesupply.com"
    
    CURRENCY = "USD"  # USD, EUR, GBP, BTC
    CURRENCY_SYMBOL = "$"
    
    RECEIPT_WIDTH = 40
    RECEIPT_FOOTER = "Thank you for shopping with us!\nReturns accepted within 30 days with receipt."
    
    # Tax rates (Berkeley, CA example)
    TAX_RATES = {
        'Berkeley': 0.1025,      # 10.25% combined city tax
        'VapeTax': 0.125,        # 12.5% vape product tax
        'State': 0.0725,         # 7.25% state base
        'Local': 0.01,           # 1% local option
        'Special': 0.00          # Special district (if applicable)
    }
    
    # Payment methods
    PAYMENT_METHODS = [
        'Cash',
        'Credit Card',
        'Debit Card',
        'Bitcoin (BTC)',
        'EBT',
        'WIC',
        'Check',
        'Store Credit',
        'Gift Card'
    ]
    
    # Database
    DB_PATH = "reggistarr.db"
    BACKUP_INTERVAL = 3600  # seconds
    
    # Security
    MANAGER_CODE = "1979"  # Default, should be changed
    REQUIRE_MANAGER_FOR = ['void', 'discount_over_20', 'no_receipt_return']


# ==================== DATA CLASSES ====================

@dataclass
class Product:
    """Product/PLU data"""
    code: str
    name: str
    price: float
    quantity: int
    department: str = "General"
    tax_rates: List[str] = None
    track_inventory: bool = True
    open_price: bool = False  # Allow price override
    cost: float = 0.0
    supplier: str = ""
    
    def __post_init__(self):
        if self.tax_rates is None:
            self.tax_rates = ['Berkeley']


@dataclass
class TransactionItem:
    """Item within a transaction"""
    plu_code: str
    name: str
    quantity: float
    unit_price: float
    tax_rate: float
    tax_amount: float
    total: float
    voided: bool = False
    discount: float = 0.0


@dataclass
class Payment:
    """Payment record"""
    method: str
    amount: float
    reference: str = ""  # Check number, BTC txid, etc.
    timestamp: datetime.datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()


@dataclass
class Transaction:
    """Complete transaction record"""
    id: str
    clerk_id: str
    clerk_name: str
    start_time: datetime.datetime
    items: List[TransactionItem]
    payments: List[Payment]
    subtotal: float
    tax_total: float
    discounts: float
    surcharges: float
    total: float
    status: str  # 'open', 'completed', 'voided', 'suspended', 'refunded'
    mode: str  # 'register', 'void', 'return', etc.
    end_time: datetime.datetime = None
    change: float = 0.0
    customer_id: str = None
    notes: str = ""


@dataclass
class Clerk:
    """Clerk/employee data"""
    id: str
    name: str
    pin: str
    permissions: List[str]
    active: bool = False
    login_time: datetime.datetime = None
    total_sales: float = 0.0
    transaction_count: int = 0


@dataclass
class Department:
    """Department/category data"""
    code: str
    name: str
    tax_rates: List[str]
    group: str = "General"
    total_sales: float = 0.0
    transaction_count: int = 0


# ==================== DATABASE MANAGER ====================

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, db_path: str = Config.DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER DEFAULT 0,
                department TEXT DEFAULT 'General',
                tax_rates TEXT DEFAULT '["Berkeley"]',
                track_inventory INTEGER DEFAULT 1,
                open_price INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                supplier TEXT DEFAULT ''
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                clerk_id TEXT NOT NULL,
                clerk_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                items TEXT NOT NULL,
                payments TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax_total REAL NOT NULL,
                discounts REAL DEFAULT 0.0,
                surcharges REAL DEFAULT 0.0,
                total REAL NOT NULL,
                status TEXT NOT NULL,
                mode TEXT NOT NULL,
                change REAL DEFAULT 0.0,
                customer_id TEXT,
                notes TEXT DEFAULT ''
            )
        ''')
        
        # Clerks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clerks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                pin TEXT NOT NULL,
                permissions TEXT NOT NULL,
                total_sales REAL DEFAULT 0.0,
                transaction_count INTEGER DEFAULT 0
            )
        ''')
        
        # Departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                tax_rates TEXT DEFAULT '["Berkeley"]',
                group_name TEXT DEFAULT 'General',
                total_sales REAL DEFAULT 0.0,
                transaction_count INTEGER DEFAULT 0
            )
        ''')
        
        # Inventory adjustments log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT NOT NULL,
                adjustment INTEGER NOT NULL,
                reason TEXT NOT NULL,
                new_quantity INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                clerk_id TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_product(self, product: Product):
        """Save product to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO products 
            (code, name, price, quantity, department, tax_rates, track_inventory, open_price, cost, supplier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product.code, product.name, product.price, product.quantity,
            product.department, json.dumps(product.tax_rates),
            int(product.track_inventory), int(product.open_price),
            product.cost, product.supplier
        ))
        conn.commit()
        conn.close()
    
    def load_products(self) -> Dict[str, Product]:
        """Load all products from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        rows = cursor.fetchall()
        conn.close()
        
        products = {}
        for row in rows:
            products[row[0]] = Product(
                code=row[0],
                name=row[1],
                price=row[2],
                quantity=row[3],
                department=row[4],
                tax_rates=json.loads(row[5]),
                track_inventory=bool(row[6]),
                open_price=bool(row[7]),
                cost=row[8],
                supplier=row[9]
            )
        return products
    
    def save_transaction(self, transaction: Transaction):
        """Save transaction to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO transactions
            (id, clerk_id, clerk_name, start_time, end_time, items, payments,
             subtotal, tax_total, discounts, surcharges, total, status, mode,
             change, customer_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.id,
            transaction.clerk_id,
            transaction.clerk_name,
            transaction.start_time.isoformat(),
            transaction.end_time.isoformat() if transaction.end_time else None,
            json.dumps([asdict(item) for item in transaction.items]),
            json.dumps([asdict(payment) for payment in transaction.payments]),
            transaction.subtotal,
            transaction.tax_total,
            transaction.discounts,
            transaction.surcharges,
            transaction.total,
            transaction.status,
            transaction.mode,
            transaction.change,
            transaction.customer_id,
            transaction.notes
        ))
        conn.commit()
        conn.close()
    
    def save_clerk(self, clerk: Clerk):
        """Save clerk to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO clerks
            (id, name, pin, permissions, total_sales, transaction_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            clerk.id, clerk.name, clerk.pin, json.dumps(clerk.permissions),
            clerk.total_sales, clerk.transaction_count
        ))
        conn.commit()
        conn.close()
    
    def load_clerks(self) -> Dict[str, Clerk]:
        """Load all clerks from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clerks')
        rows = cursor.fetchall()
        conn.close()
        
        clerks = {}
        for row in rows:
            clerks[row[0]] = Clerk(
                id=row[0],
                name=row[1],
                pin=row[2],
                permissions=json.loads(row[3]),
                total_sales=row[4],
                transaction_count=row[5]
            )
        return clerks
    
    def log_inventory_adjustment(self, product_code: str, adjustment: int, 
                                  reason: str, new_quantity: int, clerk_id: str):
        """Log inventory adjustment"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory_log
            (product_code, adjustment, reason, new_quantity, timestamp, clerk_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_code, adjustment, reason, new_quantity, 
              datetime.datetime.now().isoformat(), clerk_id))
        conn.commit()
        conn.close()


# ==================== CASH REGISTER CORE ====================

class CashRegister:
    """Main cash register system"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.products: Dict[str, Product] = {}
        self.clerks: Dict[str, Clerk] = {}
        self.departments: Dict[str, Department] = {}
        self.current_transaction: Optional[Transaction] = None
        self.current_clerk: Optional[Clerk] = None
        self.mode = "REGISTER"
        
        self.load_data()
        self.init_sample_data()
    
    def load_data(self):
        """Load data from database"""
        self.products = self.db.load_products()
        self.clerks = self.db.load_clerks()
    
    def init_sample_data(self):
        """Initialize sample data if empty"""
        if not self.products:
            # Sample products
            sample_products = [
                Product("1001", "Apple", 0.50, 100, "Produce", ["Berkeley"]),
                Product("1002", "Banana", 0.30, 150, "Produce", ["Berkeley"]),
                Product("1003", "Bread", 2.99, 50, "Bakery", ["Berkeley"]),
                Product("1004", "Milk (1gal)", 3.49, 30, "Dairy", ["Berkeley"]),
                Product("1005", "Soda (12pk)", 5.99, 40, "Beverages", ["Berkeley"]),
                Product("1006", "Vape Kit", 29.99, 20, "Vape", ["Berkeley", "VapeTax"]),
                Product("1007", "E-Liquid", 14.99, 35, "Vape", ["Berkeley", "VapeTax"]),
                Product("1008", "Repair Service", 25.00, 999, "Services", [], False, True),
            ]
            for product in sample_products:
                self.add_product(product)
        
        if not self.clerks:
            # Default clerk
            self.add_clerk(Clerk("001", "Demo Clerk", "1234", 
                               ["sale", "refund", "void", "discount"]))
    
    # ==================== PRODUCT MANAGEMENT ====================
    
    def add_product(self, product: Product):
        """Add or update product"""
        self.products[product.code] = product
        self.db.save_product(product)
    
    def get_product(self, code: str) -> Optional[Product]:
        """Get product by code"""
        return self.products.get(code)
    
    def update_stock(self, code: str, adjustment: int, reason: str) -> bool:
        """Update product stock"""
        product = self.products.get(code)
        if not product:
            return False
        
        new_quantity = product.quantity + adjustment
        if new_quantity < 0:
            return False
        
        product.quantity = new_quantity
        self.db.save_product(product)
        self.db.log_inventory_adjustment(code, adjustment, reason, 
                                         new_quantity, self.current_clerk.id if self.current_clerk else "system")
        return True
    
    # ==================== CLERK MANAGEMENT ====================
    
    def add_clerk(self, clerk: Clerk):
        """Add or update clerk"""
        self.clerks[clerk.id] = clerk
        self.db.save_clerk(clerk)
    
    def login_clerk(self, clerk_id: str, pin: str) -> bool:
        """Authenticate and login clerk"""
        clerk = self.clerks.get(clerk_id)
        if clerk and clerk.pin == pin:
            clerk.active = True
            clerk.login_time = datetime.datetime.now()
            self.current_clerk = clerk
            return True
        return False
    
    def logout_clerk(self):
        """Logout current clerk"""
        if self.current_clerk:
            self.current_clerk.active = False
            self.current_clerk.login_time = None
            self.current_clerk = None
    
    # ==================== TAX CALCULATION ====================
    
    def calculate_tax(self, amount: float, tax_rates: List[str]) -> Tuple[float, Dict]:
        """Calculate tax for given amount and rates"""
        total_tax = 0.0
        breakdown = {}
        
        for rate_name in tax_rates:
            rate = Config.TAX_RATES.get(rate_name, 0.0)
            tax = amount * rate
            total_tax += tax
            breakdown[rate_name] = {
                'rate': rate,
                'amount': tax
            }
        
        return total_tax, breakdown
    
    # ==================== TRANSACTION OPERATIONS ====================
    
    def start_transaction(self) -> Optional[Transaction]:
        """Start new transaction"""
        if not self.current_clerk:
            return None
        
        transaction_id = f"TXN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{id(self) % 10000}"
        
        self.current_transaction = Transaction(
            id=transaction_id,
            clerk_id=self.current_clerk.id,
            clerk_name=self.current_clerk.name,
            start_time=datetime.datetime.now(),
            items=[],
            payments=[],
            subtotal=0.0,
            tax_total=0.0,
            discounts=0.0,
            surcharges=0.0,
            total=0.0,
            status='open',
            mode=self.mode
        )
        
        return self.current_transaction
    
    def add_item(self, plu_code: str, quantity: float = 1.0, 
                 override_price: Optional[float] = None) -> Tuple[bool, str]:
        """Add item to current transaction"""
        if not self.current_transaction or self.current_transaction.status != 'open':
            return False, "No active transaction"
        
        product = self.products.get(plu_code)
        if not product:
            return False, f"Product not found: {plu_code}"
        
        # Check price override permission
        price = override_price if override_price is not None else product.price
        if override_price is not None and not product.open_price:
            return False, "Price override not allowed for this item"
        
        # Check stock
        if product.track_inventory and product.quantity < quantity:
            return False, f"Insufficient stock: {product.quantity} available"
        
        # Calculate tax
        item_subtotal = price * quantity
        tax_amount, tax_breakdown = self.calculate_tax(item_subtotal, product.tax_rates)
        
        # Create transaction item
        item = TransactionItem(
            plu_code=plu_code,
            name=product.name,
            quantity=quantity,
            unit_price=price,
            tax_rate=sum(Config.TAX_RATES.get(r, 0) for r in product.tax_rates),
            tax_amount=tax_amount,
            total=item_subtotal + tax_amount
        )
        
        self.current_transaction.items.append(item)
        self.recalculate_transaction()
        
        # Update inventory
        if product.track_inventory:
            self.update_stock(plu_code, -int(quantity), f"Sale - {self.current_transaction.id}")
        
        return True, f"Added: {product.name} x{quantity}"
    
    def apply_discount(self, amount: float, percentage: bool = False) -> bool:
        """Apply discount to current transaction"""
        if not self.current_transaction:
            return False
        
        if percentage:
            discount_amount = self.current_transaction.subtotal * (amount / 100)
        else:
            discount_amount = amount
        
        self.current_transaction.discounts += discount_amount
        self.recalculate_transaction()
        return True
    
    def apply_surcharge(self, amount: float, description: str, percentage: bool = False) -> bool:
        """Apply surcharge (e.g., bag fee, ATM fee)"""
        if not self.current_transaction:
            return False
        
        if percentage:
            surcharge_amount = self.current_transaction.subtotal * (amount / 100)
        else:
            surcharge_amount = amount
        
        self.current_transaction.surcharges += surcharge_amount
        self.recalculate_transaction()
        return True
    
    def void_item(self, item_index: int) -> bool:
        """Void an item from current transaction"""
        if not self.current_transaction or item_index >= len(self.current_transaction.items):
            return False
        
        item = self.current_transaction.items[item_index]
        item.voided = True
        
        # Restore inventory
        product = self.products.get(item.plu_code)
        if product and product.track_inventory:
            self.update_stock(item.plu_code, int(item.quantity), 
                            f"Void - {self.current_transaction.id}")
        
        self.recalculate_transaction()
        return True
    
    def void_transaction(self) -> bool:
        """Void entire transaction"""
        if not self.current_transaction:
            return False
        
        # Restore all inventory
        for item in self.current_transaction.items:
            if not item.voided:
                product = self.products.get(item.plu_code)
                if product and product.track_inventory:
                    self.update_stock(item.plu_code, int(item.quantity),
                                    f"Transaction Void - {self.current_transaction.id}")
        
        self.current_transaction.status = 'voided'
        self.db.save_transaction(self.current_transaction)
        self.current_transaction = None
        return True
    
    def recalculate_transaction(self):
        """Recalculate transaction totals"""
        if not self.current_transaction:
            return
        
        subtotal = 0.0
        tax = 0.0
        
        for item in self.current_transaction.items:
            if not item.voided:
                subtotal += item.unit_price * item.quantity
                tax += item.tax_amount
        
        self.current_transaction.subtotal = subtotal
        self.current_transaction.tax_total = tax
        self.current_transaction.total = (subtotal + tax - 
                                          self.current_transaction.discounts + 
                                          self.current_transaction.surcharges)
    
    def add_payment(self, method: str, amount: float, reference: str = "") -> Tuple[bool, float]:
        """Add payment to transaction"""
        if not self.current_transaction:
            return False, 0.0
        
        payment = Payment(method=method, amount=amount, reference=reference)
        self.current_transaction.payments.append(payment)
        
        total_paid = sum(p.amount for p in self.current_transaction.payments)
        remaining = self.current_transaction.total - total_paid
        
        if remaining <= 0:
            self.current_transaction.change = abs(remaining)
            self.complete_transaction()
        
        return True, remaining
    
    def complete_transaction(self):
        """Finalize transaction"""
        if not self.current_transaction:
            return
        
        self.current_transaction.status = 'completed'
        self.current_transaction.end_time = datetime.datetime.now()
        
        # Update clerk stats
        if self.current_clerk:
            self.current_clerk.total_sales += self.current_transaction.total
            self.current_clerk.transaction_count += 1
            self.db.save_clerk(self.current_clerk)
        
        # Save to database
        self.db.save_transaction(self.current_transaction)
        
        # Generate receipt
        receipt = self.generate_receipt(self.current_transaction)
        
        # Clear current transaction
        completed = self.current_transaction
        self.current_transaction = None
        
        return completed, receipt
    
    def suspend_transaction(self) -> str:
        """Suspend transaction for later recall"""
        if not self.current_transaction:
            return ""
        
        self.current_transaction.status = 'suspended'
        self.db.save_transaction(self.current_transaction)
        recall_id = self.current_transaction.id
        self.current_transaction = None
        return recall_id
    
    # ==================== RECEIPT GENERATION ====================
    
    def generate_receipt(self, transaction: Transaction) -> str:
        """Generate formatted receipt"""
        lines = []
        width = Config.RECEIPT_WIDTH
        
        # Header
        lines.append("=" * width)
        lines.append(Config.STORE_NAME.center(width))
        lines.append(Config.STORE_ADDRESS.center(width))
        lines.append(Config.STORE_PHONE.center(width))
        lines.append("=" * width)
        
        # Transaction info
        lines.append(f"Trans: {transaction.id}")
        lines.append(f"Clerk: {transaction.clerk_name}")
        lines.append(f"Date: {transaction.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("-" * width)
        
        # Items
        for i, item in enumerate(transaction.items, 1):
            if not item.voided:
                name = item.name[:20].ljust(20)
                qty = f"x{item.quantity:.0f}".rjust(4)
                price = f"${item.total:.2f}".rjust(10)
                lines.append(f"{i}. {name} {qty} {price}")
        
        lines.append("-" * width)
        
        # Totals
        lines.append(f"Subtotal: ${transaction.subtotal:.2f}".rjust(width))
        lines.append(f"Tax: ${transaction.tax_total:.2f}".rjust(width))
        
        if transaction.discounts > 0:
            lines.append(f"Discount: -${transaction.discounts:.2f}".rjust(width))
        
        if transaction.surcharges > 0:
            lines.append(f"Surcharge: ${transaction.surcharges:.2f}".rjust(width))
        
        lines.append(f"TOTAL: ${transaction.total:.2f}".rjust(width))
        lines.append("-" * width)
        
        # Payments
        for payment in transaction.payments:
            method = payment.method[:15].ljust(15)
            amount = f"${payment.amount:.2f}".rjust(15)
            lines.append(f"{method} {amount}")
        
        if transaction.change > 0:
            lines.append(f"Change: ${transaction.change:.2f}".rjust(width))
        
        # Footer
        lines.append("=" * width)
        lines.append(Config.RECEIPT_FOOTER)
        lines.append("=" * width)
        
        return "\n".join(lines)
    
    # ==================== REPORTING ====================

    def generate_z_report(self) -> str:
        """Generate end-of-day Z report"""
        today = datetime.datetime.now().date()
        start = datetime.datetime.combine(today, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get today's transactions
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE start_time BETWEEN ? AND ? AND status = 'completed'
        ''', (start.isoformat(), end.isoformat()))
        
        transactions = cursor.fetchall()
        conn.close()
        
        # Calculate totals
        total_sales = sum(t[11] for t in transactions)  # total column
        total_tax = sum(t[9] for t in transactions)     # tax_total column
        total_discounts = sum(t[10] for t in transactions)  # discounts column
        
        payment_totals = {}
        for t in transactions:
            payments = json.loads(t[6])
            for p in payments:
                method = p['method']
                payment_totals[method] = payment_totals.get(method, 0) + p['amount']
        
        # Build report
        lines = []
        lines.append("=" * 40)
        lines.append("Z-REPORT (End of Day)".center(40))
        lines.append(f"Date: {today.strftime('%Y-%m-%d')}".center(40))
        lines.append("=" * 40)
        lines.append("")
        lines.append(f"Total Transactions: {len(transactions)}")
        lines.append(f"Gross Sales: ${total_sales + total_discounts:.2f}")
        lines.append(f"Discounts: ${total_discounts:.2f}")
        lines.append(f"Net Sales: ${total_sales:.2f}")
        lines.append(f"Tax Collected: ${total_tax:.2f}")
        lines.append("")
        lines.append("Payment Methods:")
        for method, amount in payment_totals.items():
            lines.append(f"  {method}: ${amount:.2f}")
        lines.append("")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def get_low_stock_items(self, threshold: int = 10) -> List[Product]:
        """Get items with low inventory"""
        low_stock = []
        for product in self.products.values():
            if product.track_inventory and product.quantity <= threshold:
                low_stock.append(product)
        return low_stock


# ==================== CONSOLE INTERFACE ====================

def run_console_interface():
    """Run rEGGIsTARR in console mode"""
    register = CashRegister()
    
    print("=" * 50)
    print("rEGGIsTARR - Retail Electronic Goods & General")
    print("             Inventory Transaction and Receipt Recorder")
    print("=" * 50)
    print()
    
    # Login
    while not register.current_clerk:
        print("Please login:")
        clerk_id = input("Clerk ID: ")
        pin = input("PIN: ")
        if register.login_clerk(clerk_id, pin):
            print(f"\nWelcome, {register.current_clerk.name}!\n")
        else:
            print("Invalid credentials. Try again.\n")
    
    # Main loop
    while True:
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1. New Transaction")
        print("2. Product Lookup")
        print("3. Inventory Management")
        print("4. Reports")
        print("5. Logout")
        print("6. Exit")
        print()
        
        choice = input("Select option: ").strip()
        
        if choice == "1":
            run_transaction_mode(register)
        elif choice == "2":
            run_product_lookup(register)
        elif choice == "3":
            run_inventory_management(register)
        elif choice == "4":
            run_reports(register)
        elif choice == "5":
            register.logout_clerk()
            print("\nLogged out.")
            # Re-login
            while not register.current_clerk:
                clerk_id = input("Clerk ID: ")
                pin = input("PIN: ")
                if register.login_clerk(clerk_id, pin):
                    print(f"\nWelcome, {register.current_clerk.name}!\n")
                    break
                else:
                    print("Invalid credentials.\n")
        elif choice == "6":
            print("\nGoodbye!")
            break
        else:
            print("Invalid option.")


def run_transaction_mode(register: CashRegister):
    """Run transaction processing mode"""
    if not register.start_transaction():
        print("Failed to start transaction.")
        return
    
    print("\n" + "=" * 50)
    print("TRANSACTION MODE")
    print("=" * 50)
    print("Commands: [PLU] [QTY] | DISC [AMT] | VOID [ITEM#] | PAY | SUSPEND | CANCEL")
    print()
    
    while register.current_transaction and register.current_transaction.status == 'open':
        # Show current items
        if register.current_transaction.items:
            print("\nCurrent Items:")
            for i, item in enumerate(register.current_transaction.items, 1):
                status = "VOIDED" if item.voided else ""
                print(f"  {i}. {item.name} x{item.quantity} = ${item.total:.2f} {status}")
            print(f"\nSubtotal: ${register.current_transaction.subtotal:.2f}")
            print(f"Tax: ${register.current_transaction.tax_total:.2f}")
            print(f"TOTAL: ${register.current_transaction.total:.2f}")
        
        cmd = input("\n> ").strip().upper()
        
        if not cmd:
            continue
        
        parts = cmd.split()
        
        if parts[0] == "DISC":
            # Apply discount
            try:
                amount = float(parts[1])
                register.apply_discount(amount, '%' in cmd)
                print(f"Discount applied: ${amount}")
            except (ValueError, IndexError):
                print("Usage: DISC [AMOUNT] [%]")
        
        elif parts[0] == "VOID":
            # Void item
            try:
                item_num = int(parts[1]) - 1
                if register.void_item(item_num):
                    print("Item voided.")
                else:
                    print("Invalid item number.")
            except (ValueError, IndexError):
                print("Usage: VOID [ITEM_NUMBER]")
        
        elif parts[0] == "PAY":
            # Process payment
            print("\nPayment Methods:")
            for i, method in enumerate(Config.PAYMENT_METHODS, 1):
                print(f"  {i}. {method}")
            
            try:
                method_choice = int(input("Select payment method: ")) - 1
                method = Config.PAYMENT_METHODS[method_choice]
                amount = float(input(f"Amount ({method}): $"))
                
                success, remaining = register.add_payment(method, amount)
                if success:
                    if remaining > 0:
                        print(f"Remaining: ${remaining:.2f}")
                    else:
                        print("\n" + "=" * 40)
                        print("TRANSACTION COMPLETE")
                        print("=" * 40)
                        # Show receipt
                        completed, receipt = register.complete_transaction()
                        print(receipt)
                        break
            except (ValueError, IndexError):
                print("Invalid input.")
        
        elif parts[0] == "SUSPEND":
            recall_id = register.suspend_transaction()
            print(f"Transaction suspended. Recall ID: {recall_id}")
            break
        
        elif parts[0] == "CANCEL":
            register.void_transaction()
            print("Transaction cancelled.")
            break
        
        else:
            # Assume PLU code entry
            try:
                plu = parts[0]
                qty = float(parts[1]) if len(parts) > 1 else 1.0
                success, msg = register.add_item(plu, qty)
                print(msg)
            except (ValueError, IndexError):
                print("Usage: [PLU_CODE] [QUANTITY] or see commands above.")


def run_product_lookup(register: CashRegister):
    """Product lookup mode"""
    print("\n" + "=" * 50)
    print("PRODUCT LOOKUP")
    print("=" * 50)
    
    query = input("Enter PLU code or name: ").strip()
    
    # Search by code
    product = register.get_product(query)
    if product:
        print(f"\nProduct Found:")
        print(f"  Code: {product.code}")
        print(f"  Name: {product.name}")
        print(f"  Price: ${product.price:.2f}")
        print(f"  Stock: {product.quantity}")
        print(f"  Department: {product.department}")
        print(f"  Tax: {', '.join(product.tax_rates)}")
        return
    
    # Search by name
    matches = [p for p in register.products.values() if query.lower() in p.name.lower()]
    if matches:
        print(f"\nFound {len(matches)} match(es):")
        for p in matches:
            print(f"  {p.code}: {p.name} - ${p.price:.2f} ({p.quantity} in stock)")
    else:
        print("No products found.")


def run_inventory_management(register: CashRegister):
    """Inventory management mode"""
    print("\n" + "=" * 50)
    print("INVENTORY MANAGEMENT")
    print("=" * 50)
    print("1. View Low Stock")
    print("2. Adjust Stock")
    print("3. Add New Product")
    print("4. Back")
    
    choice = input("\nSelect: ").strip()
    
    if choice == "1":
        threshold = int(input("Low stock threshold (default 10): ") or "10")
        items = register.get_low_stock_items(threshold)
        if items:
            print(f"\nLow Stock Items (≤{threshold}):")
            for item in items:
                print(f"  {item.code}: {item.name} - {item.quantity} remaining")
        else:
            print("No low stock items.")
    
    elif choice == "2":
        plu = input("PLU code: ").strip()
        adjustment = int(input("Adjustment (+/-): "))
        reason = input("Reason: ").strip()
        if register.update_stock(plu, adjustment, reason):
            print("Stock updated.")
        else:
            print("Failed to update stock.")
    
    elif choice == "3":
        print("\nAdd New Product:")
        code = input("PLU Code: ").strip()
        name = input("Name: ").strip()
        price = float(input("Price: $"))
        qty = int(input("Initial Quantity: "))
        dept = input("Department: ").strip() or "General"
        
        product = Product(code, name, price, qty, dept)
        register.add_product(product)
        print(f"Product {name} added.")


def run_reports(register: CashRegister):
    """Reports mode"""
    print("\n" + "=" * 50)
    print("REPORTS")
    print("=" * 50)
    print("1. Z-Report (End of Day)")
    print("2. Clerk Performance")
    print("3. Department Sales")
    print("4. Back")
    
    choice = input("\nSelect: ").strip()
    
    if choice == "1":
        report = register.generate_z_report()
        print("\n" + report)
        
        save = input("\nSave to file? (y/n): ").lower()
        if save == 'y':
            filename = f"zreport_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
            with open(filename, 'w') as f:
                f.write(report)
            print(f"Saved to {filename}")
    
    elif choice == "2":
        print("\nClerk Performance:")
        for clerk in register.clerks.values():
            print(f"  {clerk.name}: ${clerk.total_sales:.2f} ({clerk.transaction_count} transactions)")
    
    elif choice == "3":
        print("\nDepartment Sales:")
        # This would aggregate from transactions in a full implementation
        print("Feature: Aggregate sales by department")


# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    try:
        run_console_interface()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
