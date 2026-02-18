#!/usr/bin/env python3
"""
ReggieStarr Core - Simplified POS System
Clean reference implementation for porting to other languages

This version strips away advanced features to show the core architecture.
Use this as the basis for C#, C++, or other language ports.

Features included:
- Basic transaction processing
- Product/PLU management
- Tax calculation
- Payment handling
- Receipt generation
- SQLite persistence
"""

import sqlite3
import datetime
import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import json

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
    tax_rates: List[str] = None
    quantity: int = 0
    
    def __post_init__(self):
        if self.tax_rates is None:
            self.tax_rates = []

@dataclass
class TransactionItem:
    """A line item in a transaction"""
    plu_code: str
    name: str
    quantity: float
    unit_price: float
    tax_amount: float = 0.0
    total: float = 0.0

@dataclass
class Transaction:
    """A sales transaction"""
    id: str
    clerk_name: str
    start_time: datetime.datetime
    items: List[TransactionItem]
    payments: List[Dict]
    subtotal: float
    tax_total: float
    total: float
    status: str = "active"
    
    def __post_init__(self):
        if isinstance(self.start_time, str):
            self.start_time = datetime.datetime.fromisoformat(self.start_time)

# ============================================================================
# CORE REGISTER CLASS
# ============================================================================

class CashRegister:
    """Main cash register logic - port this class first"""
    
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
                quantity INTEGER DEFAULT 0
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                clerk_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                items TEXT NOT NULL,
                payments TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax_total REAL NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'completed'
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
            INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?)
        ''', (product.plu_code, product.name, product.price, 
              product.department, json.dumps(product.tax_rates), product.quantity))
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
                quantity=row[5]
            )
        return None
    
    # ========================================================================
    # TRANSACTION OPERATIONS
    # ========================================================================
    
    def start_transaction(self) -> Transaction:
        """Start a new transaction"""
        self.current_transaction = Transaction(
            id=str(uuid.uuid4())[:8].upper(),
            clerk_name=self.current_clerk or "Unknown",
            start_time=datetime.datetime.now(),
            items=[],
            payments=[],
            subtotal=0.0,
            tax_total=0.0,
            total=0.0
        )
        return self.current_transaction
    
    def add_item(self, plu_code: str, quantity: float = 1.0) -> Tuple[bool, str]:
        """Add an item to the current transaction"""
        if not self.current_transaction:
            self.start_transaction()
        
        product = self.get_product(plu_code)
        if not product:
            return False, f"Product {plu_code} not found"
        
        # Calculate item totals
        line_total = product.price * quantity
        tax_amount = self._calculate_tax(line_total, product.tax_rates)
        
        item = TransactionItem(
            plu_code=plu_code,
            name=product.name,
            quantity=quantity,
            unit_price=product.price,
            tax_amount=tax_amount,
            total=line_total + tax_amount
        )
        
        self.current_transaction.items.append(item)
        self._recalculate_totals()
        
        return True, f"Added {product.name} x{quantity}"
    
    def _calculate_tax(self, amount: float, tax_rates: List[str]) -> float:
        """Calculate tax for an amount"""
        total_tax = 0.0
        for rate_name in tax_rates:
            if rate_name in self.TAX_RATES:
                total_tax += amount * self.TAX_RATES[rate_name]
        return total_tax
    
    def _recalculate_totals(self):
        """Recalculate transaction totals"""
        if not self.current_transaction:
            return
        
        subtotal = sum(item.unit_price * item.quantity for item in self.current_transaction.items)
        tax = sum(item.tax_amount for item in self.current_transaction.items)
        
        self.current_transaction.subtotal = subtotal
        self.current_transaction.tax_total = tax
        self.current_transaction.total = subtotal + tax
    
    def add_payment(self, method: str, amount: float) -> Tuple[bool, float]:
        """Add a payment to the transaction"""
        if not self.current_transaction:
            return False, 0.0
        
        payment = {
            'method': method,
            'amount': amount,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.current_transaction.payments.append(payment)
        
        total_paid = sum(p['amount'] for p in self.current_transaction.payments)
        remaining = self.current_transaction.total - total_paid
        
        if remaining <= 0:
            self._complete_transaction()
        
        return True, remaining
    
    def _complete_transaction(self):
        """Finalize the transaction"""
        if not self.current_transaction:
            return
        
        self.current_transaction.status = 'completed'
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.current_transaction.id,
            self.current_transaction.clerk_name,
            self.current_transaction.start_time.isoformat(),
            json.dumps([asdict(item) for item in self.current_transaction.items]),
            json.dumps(self.current_transaction.payments),
            self.current_transaction.subtotal,
            self.current_transaction.tax_total,
            self.current_transaction.total,
            self.current_transaction.status
        ))
        conn.commit()
        conn.close()
    
    def void_transaction(self) -> bool:
        """Void the current transaction"""
        if self.current_transaction:
            self.current_transaction.status = 'voided'
            self.current_transaction = None
            return True
        return False
    
    # ========================================================================
    # RECEIPT GENERATION
    # ========================================================================
    
    def generate_receipt(self) -> str:
        """Generate a text receipt for the current transaction"""
        if not self.current_transaction:
            return "No active transaction"
        
        lines = [
            "=" * 40,
            "    REGGIESTARR POS",
            "    Performance Supply Depot",
            "=" * 40,
            f"Transaction: {self.current_transaction.id}",
            f"Clerk: {self.current_transaction.clerk_name}",
            f"Date: {self.current_transaction.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 40,
        ]
        
        for item in self.current_transaction.items:
            lines.append(f"{item.name[:20]:20s} {item.quantity:>6.1f} ${item.total:>8.2f}")
        
        lines.extend([
            "-" * 40,
            f"{'Subtotal:':30s} ${self.current_transaction.subtotal:>8.2f}",
            f"{'Tax:':30s} ${self.current_transaction.tax_total:>8.2f}",
            f"{'TOTAL:':30s} ${self.current_transaction.total:>8.2f}",
            "-" * 40,
        ])
        
        for payment in self.current_transaction.payments:
            lines.append(f"{payment['method']:20s} ${payment['amount']:>8.2f}")
        
        total_paid = sum(p['amount'] for p in self.current_transaction.payments)
        change = total_paid - self.current_transaction.total
        if change > 0:
            lines.append(f"{'Change:':30s} ${change:>8.2f}")
        
        lines.extend([
            "=" * 40,
            "    Thank you for shopping!",
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
        
        total_sales = sum(row[7] for row in rows)
        total_tax = sum(row[6] for row in rows)
        
        lines = [
            "SALES REPORT",
            f"Period: {start_date.date()} to {end_date.date()}",
            f"Transactions: {len(rows)}",
            f"Total Sales: ${total_sales:.2f}",
            f"Total Tax: ${total_tax:.2f}",
        ]
        
        return "\n".join(lines)


# ============================================================================
# SIMPLE CLI INTERFACE
# ============================================================================

def run_cli():
    """Simple command-line interface for testing"""
    register = CashRegister()
    
    # Add sample products
    register.add_product(Product("1001", "Apple", 0.50, "Produce", ["Standard"], 100))
    register.add_product(Product("1002", "Sandwich", 5.99, "Food", ["Berkeley"], 50))
    register.add_product(Product("1003", "Vape Pen", 19.99, "Tobacco", ["Berkeley", "Vape"], 25))
    
    print("ReggieStarr Core - Test Interface")
    print("Commands: login, add, pay, receipt, report, quit")
    
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
            success, msg = register.add_item(plu, qty)
            print(msg)
        elif cmd == "pay":
            method = input("Payment Method: ")
            amount = float(input("Amount: "))
            success, remaining = register.add_payment(method, amount)
            print(f"Remaining: ${remaining:.2f}")
        elif cmd == "receipt":
            print(register.generate_receipt())
        elif cmd == "report":
            end = datetime.datetime.now()
            start = end - datetime.timedelta(days=1)
            print(register.generate_sales_report(start, end))
        else:
            print("Unknown command")


if __name__ == "__main__":
    run_cli()
