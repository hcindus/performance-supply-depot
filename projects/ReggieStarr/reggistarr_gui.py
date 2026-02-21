#!/usr/bin/env python3
"""
ReggieStarr GUI - Full Tkinter Interface for TEC MA-79 Digital Cash Register
Complete Point-of-Sale System with Touchscreen Interface

Author: Performance Supply Depot LLC
Version: 4.1.0
Date: February 18, 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import json
import sqlite3
import urllib.request
import urllib.error
import sys
import time
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# Optional imports for advanced features
try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# Optional sound for bell/alert
try:
    import winsound  # Windows
    SOUND_AVAILABLE = True
except ImportError:
    try:
        import subprocess  # Linux/macOS
        SOUND_AVAILABLE = True
    except ImportError:
        SOUND_AVAILABLE = False

# ==================== CONFIGURATION ====================

class Config:
    STORE_NAME = "Performance Supply Depot"
    STORE_ADDRESS = "123 Main Street, Berkeley, CA 94702"
    STORE_PHONE = "(510) 555-0123"
    
    CURRENCY_SYMBOL = "$"
    
    # TEC MA-79 Style Tax Rates
    TAX_RATES = {
        'Berkeley': 0.1025,
        'VapeTax': 0.125,
        'State': 0.0725,
        'Local': 0.01,
    }
    
    # CRV (California Redemption Value) Rates
    CRV_RATES = {
        0.05: "Small Bottle (≤24oz)",
        0.10: "Large Bottle (>24oz)",
    }
    
    PAYMENT_METHODS = [
        'Cash', 'Credit Card', 'Debit Card', 'Bitcoin (BTC)',
        'EBT', 'WIC', 'Check', 'Store Credit', 'Gift Card'
    ]
    
    # TEC MA-79 Modes
    MODES = {
        'Register': 'Normal sales transactions',
        'Void': 'Cancel previous transactions',
        'X': 'Read reports without reset',
        'Z': 'Read and reset reports',
        'Program': 'Configure settings',
        'Service': 'Maintenance mode',
        'Negative': 'Returns and refunds'
    }
    
    # Multilingual Support
    LANGUAGES = {
        'English': {
            'product_code': 'Product Code',
            'quantity': 'Quantity',
            'price': 'Price',
            'add_product': 'Add Product',
            'discount': 'Discount',
            'surcharge': 'Surcharge',
            'payment_method': 'Payment Method',
            'refund': 'Refund',
            'void': 'Void',
            'exchange': 'Exchange',
            'cancel': 'Cancel Transaction',
            'generate_report': 'Generate Report',
            'login': 'Login',
            'logout': 'Logout',
            'split_check': 'Split Check',
            'split_tender': 'Split Tender',
            'currency_conv': 'Currency Conversion',
            'qr_code': 'QR Code',
            'pay': 'Pay',
            'hold': 'Hold',
            'recall': 'Recall',
            'subtotal': 'Subtotal',
            'tax': 'Tax',
            'total': 'TOTAL',
            'change': 'Change',
            'welcome': 'Welcome',
            'thank_you': 'Thank you for shopping with us!'
        },
        'Spanish': {
            'product_code': 'Código de Producto',
            'quantity': 'Cantidad',
            'price': 'Precio',
            'add_product': 'Agregar Producto',
            'discount': 'Descuento',
            'surcharge': 'Recargo',
            'payment_method': 'Método de Pago',
            'refund': 'Reembolso',
            'void': 'Anular',
            'exchange': 'Intercambiar',
            'cancel': 'Cancelar Transacción',
            'generate_report': 'Generar Informe',
            'login': 'Iniciar sesión',
            'logout': 'Cerrar sesión',
            'split_check': 'Dividir Cheque',
            'split_tender': 'Dividir Pago',
            'currency_conv': 'Conversión de Moneda',
            'qr_code': 'Código QR',
            'pay': 'Pagar',
            'hold': 'Espera',
            'recall': 'Recordar',
            'subtotal': 'Subtotal',
            'tax': 'Impuesto',
            'total': 'TOTAL',
            'change': 'Cambio',
            'welcome': 'Bienvenido',
            'thank_you': '¡Gracias por comprar con nosotros!'
        },
        'French': {
            'product_code': 'Code Produit',
            'quantity': 'Quantité',
            'price': 'Prix',
            'add_product': 'Ajouter Produit',
            'discount': 'Remise',
            'surcharge': 'Supplément',
            'payment_method': 'Mode de Paiement',
            'refund': 'Remboursement',
            'void': 'Annuler',
            'exchange': 'Échanger',
            'cancel': 'Annuler Transaction',
            'generate_report': 'Générer Rapport',
            'login': 'Connexion',
            'logout': 'Déconnexion',
            'split_check': 'Diviser Addition',
            'split_tender': 'Paiement Partagé',
            'currency_conv': 'Conversion Devise',
            'qr_code': 'Code QR',
            'pay': 'Payer',
            'hold': 'En Attente',
            'recall': 'Rappeler',
            'subtotal': 'Sous-total',
            'tax': 'Taxe',
            'total': 'TOTAL',
            'change': 'Monnaie',
            'welcome': 'Bienvenue',
            'thank_you': 'Merci de votre visite!'
        }
    }
    
    # Currency Exchange Rates (base: USD)
    EXCHANGE_RATES = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.75,
        'BTC': 0.000022,
        'JPY': 110.0,
        'CAD': 1.25,
        'AUD': 1.35
    }
    
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'BTC': '₿',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$'
    }


# ==================== DATA CLASSES ====================

@dataclass
class Product:
    code: str
    name: str
    price: float
    quantity: int
    department: str = "General"
    tax_rates: List[str] = None
    track_inventory: bool = True
    open_price: bool = False
    plu_code: str = None
    crv_applicable: bool = False
    crv_rate: float = 0.0
    
    def __post_init__(self):
        if self.tax_rates is None:
            self.tax_rates = ['Berkeley']


@dataclass
class TransactionItem:
    plu_code: str
    name: str
    quantity: float
    unit_price: float
    tax_rate: float
    tax_amount: float
    crv_amount: float
    total: float
    voided: bool = False
    discount: float = 0.0


@dataclass
class Transaction:
    id: str
    clerk_id: str
    clerk_name: str
    start_time: datetime.datetime
    items: List[TransactionItem]
    payments: List[Dict]
    subtotal: float
    tax_total: float
    crv_total: float
    discounts: float
    surcharges: float
    total: float
    status: str
    mode: str
    end_time: datetime.datetime = None
    change: float = 0.0


# ==================== DATABASE ====================

class DatabaseManager:
    def __init__(self, db_path: str = "reggistarr.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
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
                plu_code TEXT,
                crv_applicable INTEGER DEFAULT 0,
                crv_rate REAL DEFAULT 0
            )
        ''')
        
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
                crv_total REAL DEFAULT 0,
                discounts REAL DEFAULT 0,
                surcharges REAL DEFAULT 0,
                total REAL NOT NULL,
                status TEXT NOT NULL,
                mode TEXT NOT NULL,
                change REAL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clerks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                pin TEXT NOT NULL,
                permissions TEXT NOT NULL,
                active INTEGER DEFAULT 0,
                total_sales REAL DEFAULT 0,
                transaction_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()


# ==================== CASH REGISTER CORE ====================

class CashRegister:
    def __init__(self):
        self.db = DatabaseManager()
        self.products: Dict[str, Product] = {}
        self.clerks: Dict[str, dict] = {}
        self.current_transaction: Optional[Transaction] = None
        self.current_clerk: Optional[dict] = None
        self.mode = "Register"
        self.load_data()
        self.init_sample_data()
        
        # TEC MA-79 Functions
        self.functions = {
            'Feed': self.feed,
            'Item Correct': self.item_correct,
            'Return': self.return_merchandise,
            'Multiplier': self.multiplier,
            'PLU': self.plu_lookup,
            'No Sale': self.no_sale,
            'Tax Mod': self.tax_modifier,
            'Discount': self.discount,
            'Bag Fee': self.bag_fee,
            'ATM Fee': self.atm_fee,
            'RA': self.received_on_account,
            'PO': self.paid_out,
            'Price Inquiry': self.price_inquiry,
            'Price Change': self.price_change,
            'Subtotal': self.show_subtotal,
            'Total': self.show_total,
            'CRV': self.bottle_fee,
            'Clear': self.clear_entry,
            'Enter': self.enter_item,
        }
    
    def load_data(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products')
        for row in cursor.fetchall():
            self.products[row[0]] = Product(
                code=row[0], name=row[1], price=row[2], quantity=row[3],
                department=row[4], tax_rates=json.loads(row[5]),
                track_inventory=bool(row[6]), open_price=bool(row[7]),
                plu_code=row[8], crv_applicable=bool(row[9]), crv_rate=row[10]
            )
        
        cursor.execute('SELECT * FROM clerks')
        for row in cursor.fetchall():
            self.clerks[row[0]] = {
                'id': row[0], 'name': row[1], 'pin': row[2],
                'permissions': json.loads(row[3]), 'active': bool(row[4]),
                'total_sales': row[5], 'transaction_count': row[6]
            }
        
        conn.close()
    
    def init_sample_data(self):
        if not self.products:
            samples = [
                Product("1001", "Apple", 0.50, 100, "Produce", ["Berkeley"]),
                Product("1002", "Banana", 0.30, 150, "Produce", ["Berkeley"]),
                Product("1003", "Soda (12pk)", 5.99, 40, "Beverages", ["Berkeley"], crv_applicable=True, crv_rate=0.10),
                Product("1004", "Vape Kit", 29.99, 20, "Vape", ["Berkeley", "VapeTax"]),
                Product("1005", "E-Liquid", 14.99, 35, "Vape", ["Berkeley", "VapeTax"]),
                Product("1006", "Water Bottle", 1.29, 60, "Beverages", ["Berkeley"], crv_applicable=True, crv_rate=0.05),
                Product("1007", "Repair Service", 25.00, 999, "Services", [], open_price=True),
            ]
            for p in samples:
                self.add_product(p)
        
        if not self.clerks:
            self.add_clerk({'id': '001', 'name': 'Demo Clerk', 'pin': '1234',
                          'permissions': ['sale', 'refund', 'void', 'discount']})
    
    def add_product(self, product: Product):
        self.products[product.code] = product
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product.code, product.name, product.price, product.quantity,
              product.department, json.dumps(product.tax_rates),
              int(product.track_inventory), int(product.open_price),
              product.plu_code, int(product.crv_applicable), product.crv_rate))
        conn.commit()
        conn.close()
    
    def add_clerk(self, clerk: dict):
        self.clerks[clerk['id']] = clerk
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO clerks VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (clerk['id'], clerk['name'], clerk['pin'], json.dumps(clerk['permissions']),
              int(clerk.get('active', False)), clerk.get('total_sales', 0),
              clerk.get('transaction_count', 0)))
        conn.commit()
        conn.close()
    
    def login_clerk(self, clerk_id: str, pin: str) -> bool:
        clerk = self.clerks.get(clerk_id)
        if clerk and clerk['pin'] == pin:
            clerk['active'] = True
            self.current_clerk = clerk
            return True
        return False
    
    def calculate_tax(self, amount: float, tax_rates: List[str]) -> Tuple[float, Dict]:
        total_tax = 0.0
        breakdown = {}
        for rate_name in tax_rates:
            rate = Config.TAX_RATES.get(rate_name, 0.0)
            tax = amount * rate
            total_tax += tax
            breakdown[rate_name] = {'rate': rate, 'amount': tax}
        return total_tax, breakdown
    
    def start_transaction(self) -> Optional[Transaction]:
        if not self.current_clerk:
            return None
        
        txn_id = f"TXN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{id(self) % 10000}"
        self.current_transaction = Transaction(
            id=txn_id,
            clerk_id=self.current_clerk['id'],
            clerk_name=self.current_clerk['name'],
            start_time=datetime.datetime.now(),
            items=[],
            payments=[],
            subtotal=0.0,
            tax_total=0.0,
            crv_total=0.0,
            discounts=0.0,
            surcharges=0.0,
            total=0.0,
            status='open',
            mode=self.mode
        )
        return self.current_transaction
    
    def add_item(self, plu_code: str, quantity: float = 1.0, 
                 override_price: Optional[float] = None) -> Tuple[bool, str]:
        if not self.current_transaction or self.current_transaction.status != 'open':
            return False, "No active transaction"
        
        product = self.products.get(plu_code)
        if not product:
            return False, f"Product not found: {plu_code}"
        
        price = override_price if override_price is not None else product.price
        if override_price and not product.open_price:
            return False, "Price override not allowed"
        
        if product.track_inventory and product.quantity < quantity:
            return False, f"Insufficient stock: {product.quantity} available"
        
        item_subtotal = price * quantity
        tax_amount, _ = self.calculate_tax(item_subtotal, product.tax_rates)
        crv_amount = product.crv_rate * quantity if product.crv_applicable else 0.0
        
        item = TransactionItem(
            plu_code=plu_code,
            name=product.name,
            quantity=quantity,
            unit_price=price,
            tax_rate=sum(Config.TAX_RATES.get(r, 0) for r in product.tax_rates),
            tax_amount=tax_amount,
            crv_amount=crv_amount,
            total=item_subtotal + tax_amount + crv_amount
        )
        
        self.current_transaction.items.append(item)
        self.recalculate_transaction()
        
        if product.track_inventory:
            product.quantity -= int(quantity)
            self.add_product(product)
        
        return True, f"Added: {product.name} x{quantity}"
    
    def recalculate_transaction(self):
        if not self.current_transaction:
            return
        
        subtotal = 0.0
        tax = 0.0
        crv = 0.0
        
        for item in self.current_transaction.items:
            if not item.voided:
                subtotal += item.unit_price * item.quantity
                tax += item.tax_amount
                crv += item.crv_amount
        
        self.current_transaction.subtotal = subtotal
        self.current_transaction.tax_total = tax
        self.current_transaction.crv_total = crv
        self.current_transaction.total = (subtotal + tax + crv - 
                                          self.current_transaction.discounts + 
                                          self.current_transaction.surcharges)
    
    def void_item(self, index: int) -> bool:
        if not self.current_transaction or index >= len(self.current_transaction.items):
            return False
        
        item = self.current_transaction.items[index]
        item.voided = True
        
        product = self.products.get(item.plu_code)
        if product and product.track_inventory:
            product.quantity += int(item.quantity)
            self.add_product(product)
        
        self.recalculate_transaction()
        return True
    
    def add_payment(self, method: str, amount: float) -> Tuple[bool, float]:
        if not self.current_transaction:
            return False, 0.0
        
        payment = {'method': method, 'amount': amount, 
                  'timestamp': datetime.datetime.now().isoformat()}
        self.current_transaction.payments.append(payment)
        
        total_paid = sum(p['amount'] for p in self.current_transaction.payments)
        remaining = self.current_transaction.total - total_paid
        
        if remaining <= 0:
            self.current_transaction.change = abs(remaining)
            self.complete_transaction()
        
        return True, remaining
    
    def set_mode(self, mode: str) -> bool:
        """Set TEC MA-79 operating mode"""
        if mode in Config.MODES:
            self.mode = mode
            return True
        return False
    
    def generate_group_report(self) -> str:
        """Generate sales report by department/group"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT items FROM transactions WHERE status = 'completed'
        ''')
        
        group_sales = defaultdict(float)
        for row in cursor.fetchall():
            items = json.loads(row[0])
            for item in items:
                if not item.get('voided', False):
                    # Get department from product
                    product = self.products.get(item.get('plu_code', ''))
                    dept = product.department if product else 'Unknown'
                    group_sales[dept] += item.get('total', 0)
        
        conn.close()
        
        report_lines = ["Group/Department Sales Report", "=" * 40]
        for dept, total in sorted(group_sales.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"{dept:20s} ${total:10.2f}")
        
        return "\n".join(report_lines)
    
    def generate_plu_report(self) -> str:
        """Generate sales report by PLU"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT items FROM transactions WHERE status = 'completed'
        ''')
        
        plu_sales = defaultdict(lambda: {'quantity': 0, 'total': 0.0})
        for row in cursor.fetchall():
            items = json.loads(row[0])
            for item in items:
                if not item.get('voided', False):
                    plu = item.get('plu_code', 'Unknown')
                    plu_sales[plu]['quantity'] += item.get('quantity', 0)
                    plu_sales[plu]['total'] += item.get('total', 0)
        
        conn.close()
        
        report_lines = ["PLU Sales Report", "=" * 50]
        report_lines.append(f"{'PLU':10s} {'Name':20s} {'Qty':>8s} {'Total':>10s}")
        report_lines.append("-" * 50)
        
        for plu, data in sorted(plu_sales.items(), key=lambda x: x[1]['total'], reverse=True):
            product = self.products.get(plu)
            name = product.name if product else 'Unknown'
            report_lines.append(f"{plu:10s} {name[:20]:20s} {data['quantity']:8.1f} ${data['total']:9.2f}")
        
        return "\n".join(report_lines)
    
    def generate_period_report(self, period_type: str = 'hourly') -> str:
        """Generate sales report by time period"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT start_time, total FROM transactions WHERE status = 'completed'
        ''')
        
        period_sales = defaultdict(float)
        for row in cursor.fetchall():
            timestamp = datetime.datetime.fromisoformat(row[0])
            total = row[1]
            
            if period_type == 'hourly':
                key = timestamp.strftime('%H:00')
            elif period_type == 'daily':
                key = timestamp.strftime('%Y-%m-%d')
            elif period_type == 'weekly':
                key = timestamp.strftime('%Y-W%W')
            elif period_type == 'monthly':
                key = timestamp.strftime('%Y-%m')
            else:
                key = timestamp.strftime('%Y-%m-%d %H:00')
            
            period_sales[key] += total
        
        conn.close()
        
        report_lines = [f"{period_type.capitalize()} Sales Report", "=" * 40]
        for period, total in sorted(period_sales.items()):
            report_lines.append(f"{period:20s} ${total:10.2f}")
        
        return "\n".join(report_lines)
    
    def generate_sales_totals(self, periods: List[str] = None) -> str:
        """Generate sales totals for multiple time periods"""
        if periods is None:
            periods = ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year']
        
        now = datetime.datetime.now()
        period_deltas = {
            '1 day': datetime.timedelta(days=1),
            '1 week': datetime.timedelta(weeks=1),
            '3 weeks': datetime.timedelta(weeks=3),
            '1 month': datetime.timedelta(days=30),
            '3 months': datetime.timedelta(days=90),
            '6 months': datetime.timedelta(days=180),
            '1 year': datetime.timedelta(days=365),
        }
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        report_lines = ["Sales Totals Report", "=" * 40]
        
        for period in periods:
            delta = period_deltas.get(period, datetime.timedelta(days=1))
            start_date = now - delta
            
            cursor.execute('''
                SELECT SUM(total), COUNT(*) FROM transactions 
                WHERE start_time >= ? AND status = 'completed'
            ''', (start_date.isoformat(),))
            
            row = cursor.fetchone()
            total_sales = row[0] if row[0] else 0.0
            count = row[1] if row[1] else 0
            
            report_lines.append(f"{period:15s} ${total_sales:10.2f} ({count} transactions)")
        
        conn.close()
        return "\n".join(report_lines)
    
    def complete_transaction(self):
        if not self.current_transaction:
            return
        
        self.current_transaction.status = 'completed'
        self.current_transaction.end_time = datetime.datetime.now()
        
        if self.current_clerk:
            self.current_clerk['total_sales'] += self.current_transaction.total
            self.current_clerk['transaction_count'] += 1
            self.add_clerk(self.current_clerk)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.current_transaction.id, self.current_transaction.clerk_id,
              self.current_transaction.clerk_name,
              self.current_transaction.start_time.isoformat(),
              self.current_transaction.end_time.isoformat(),
              json.dumps([asdict(item) for item in self.current_transaction.items]),
              json.dumps(self.current_transaction.payments),
              self.current_transaction.subtotal, self.current_transaction.tax_total,
              self.current_transaction.crv_total, self.current_transaction.discounts,
              self.current_transaction.surcharges, self.current_transaction.total,
              self.current_transaction.status, self.current_transaction.mode,
              self.current_transaction.change))
        conn.commit()
        conn.close()
    
    # TEC MA-79 Function Implementations
    def feed(self): pass
    def item_correct(self): pass
    def return_merchandise(self): pass
    def multiplier(self): pass
    def plu_lookup(self): pass
    def no_sale(self):
        """No Sale - Open drawer and ring bell"""
        result = "Drawer opened"
        
        # Ring the bell (for attention)
        self.ring_bell(pattern="no_sale")
        
        return result
    
    def ring_bell(self, pattern: str = "short"):
        """Ring the POS bell
        Patterns: short, long, double, triple, no_sale, alert, error
        """
        try:
            if sys.platform == "win32":
                import winsound
                if pattern == "no_sale":
                    winsound.MessageBeep(winsound.MB_OK)
                elif pattern == "error":
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                else:
                    winsound.Beep(1000, 200)
            else:
                # Linux/macOS - use beep or aplay
                import subprocess
                freq = 1000
                duration = 200
                count = 1
                
                if pattern == "no_sale":
                    count = 2
                    duration = 150
                elif pattern == "double":
                    count = 2
                elif pattern == "triple":
                    count = 3
                elif pattern == "error":
                    freq = 500
                    duration = 300
                    count = 3
                
                for _ in range(count):
                    try:
                        subprocess.run(['beep', '-f', str(freq), '-l', str(duration)], 
                                    capture_output=True, timeout=1)
                    except FileNotFoundError:
                        # beep not installed, try speaker
                        try:
                            subprocess.run(['paplay', '/usr/share/sounds/gtk-events/click.wav'],
                                        capture_output=True, timeout=1)
                        except:
                            pass  # No sound available
                    if count > 1:
                        import time
                        time.sleep(0.15)
        except Exception as e:
            pass  # Silently fail if no sound
    def tax_modifier(self): pass
    def discount(self): pass
    def bag_fee(self): pass
    def atm_fee(self): pass
    def received_on_account(self): pass
    def paid_out(self): pass
    def price_inquiry(self, plu_code: str) -> str:
        product = self.products.get(plu_code)
        if product:
            return f"{product.name}: {Config.CURRENCY_SYMBOL}{product.price:.2f}"
        return "Product not found"
    def price_change(self): pass
    def show_subtotal(self) -> float:
        return self.current_transaction.subtotal if self.current_transaction else 0.0
    def show_total(self) -> float:
        return self.current_transaction.total if self.current_transaction else 0.0
    def bottle_fee(self): pass
    def clear_entry(self): pass
    def enter_item(self): pass
    
    # Extended Features
    def process_split_tender(self, payments: List[Tuple[str, float]]) -> bool:
        """Process multiple payment methods for one transaction"""
        if not self.current_transaction:
            return False
        
        total_paid = 0.0
        for method, amount in payments:
            total_paid += amount
            self.current_transaction.payments.append({
                'method': method,
                'amount': amount,
                'timestamp': datetime.datetime.now().isoformat()
            })
        
        if total_paid >= self.current_transaction.total:
            self.current_transaction.change = total_paid - self.current_transaction.total
            self.complete_transaction()
            return True
        return False
    
    def create_layaway(self, deposit: float, customer_id: str, due_date: datetime.datetime) -> str:
        """Create layaway transaction"""
        if not self.current_transaction:
            return ""
        
        layaway_id = f"LAYAWAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS layaways (
                layaway_id TEXT PRIMARY KEY,
                transaction_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                total_amount REAL NOT NULL,
                deposit_amount REAL NOT NULL,
                balance_due REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_date TEXT NOT NULL
            )
        ''')
        
        balance = self.current_transaction.total - deposit
        cursor.execute('''
            INSERT INTO layaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (layaway_id, self.current_transaction.id, customer_id,
              self.current_transaction.total, deposit, balance,
              due_date.isoformat(), 'active', datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Mark original transaction as layaway
        self.current_transaction.status = 'layaway'
        self.db.save_transaction(self.current_transaction)
        
        return layaway_id
    
    def process_layaway_payment(self, layaway_id: str, amount: float) -> Tuple[bool, float]:
        """Make payment on layaway"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT balance_due FROM layaways WHERE layaway_id = ?', (layaway_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, 0.0
        
        current_balance = row[0]
        new_balance = current_balance - amount
        
        if new_balance <= 0:
            cursor.execute('UPDATE layaways SET balance_due = 0, status = ? WHERE layaway_id = ?',
                         ('completed', layaway_id))
        else:
            cursor.execute('UPDATE layaways SET balance_due = ? WHERE layaway_id = ?',
                         (new_balance, layaway_id))
        
        conn.commit()
        conn.close()
        
        return True, new_balance
    
    def add_customer(self, customer_id: str, name: str, email: str = "", phone: str = "") -> bool:
        """Add customer to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_date TEXT NOT NULL,
                total_purchases REAL DEFAULT 0.0,
                visit_count INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, name, email, phone, datetime.datetime.now().isoformat(), 0.0, 0))
        conn.commit()
        conn.close()
        return True
    
    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE customer_id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'customer_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'created_date': row[4],
                'total_purchases': row[5],
                'visit_count': row[6]
            }
        return None
    
    def issue_gift_card(self, card_id: str, amount: float) -> bool:
        """Issue new gift card"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gift_cards (
                card_id TEXT PRIMARY KEY,
                initial_amount REAL NOT NULL,
                balance REAL NOT NULL,
                issue_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        expiry = datetime.datetime.now() + datetime.timedelta(days=365)
        cursor.execute('''
            INSERT INTO gift_cards VALUES (?, ?, ?, ?, ?, ?)
        ''', (card_id, amount, amount, datetime.datetime.now().isoformat(),
              expiry.isoformat(), 'active'))
        conn.commit()
        conn.close()
        return True
    
    def get_gift_card_balance(self, card_id: str) -> float:
        """Check gift card balance"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM gift_cards WHERE card_id = ? AND status = ?',
                      (card_id, 'active'))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0.0
    
    def redeem_gift_card(self, card_id: str, amount: float) -> bool:
        """Redeem amount from gift card"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM gift_cards WHERE card_id = ? AND status = ?',
                      (card_id, 'active'))
        row = cursor.fetchone()
        
        if not row or row[0] < amount:
            conn.close()
            return False
        
        new_balance = row[0] - amount
        status = 'active' if new_balance > 0 else 'depleted'
        cursor.execute('UPDATE gift_cards SET balance = ?, status = ? WHERE card_id = ?',
                      (new_balance, status, card_id))
        conn.commit()
        conn.close()
        return True
    
    def generate_custom_report(self, start_date: datetime.datetime, 
                               end_date: datetime.datetime,
                               report_type: str = 'sales') -> str:
        """Generate custom date range report"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE start_time BETWEEN ? AND ? AND status = 'completed'
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        transactions = cursor.fetchall()
        conn.close()
        
        total_sales = sum(t[11] for t in transactions)
        total_tax = sum(t[9] for t in transactions)
        
        report_lines = [
            f"Custom Report: {report_type}",
            f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            f"Total Transactions: {len(transactions)}",
            f"Total Sales: ${total_sales:.2f}",
            f"Total Tax: ${total_tax:.2f}",
            "=" * 50,
        ]
        
        return "\n".join(report_lines)
    
    # Advanced Features
    def hold_transaction(self) -> str:
        """Hold current transaction for later recall"""
        if not self.current_transaction:
            return ""
        
        hold_id = f"HOLD-{datetime.datetime.now().strftime('%H%M%S')}"
        self.current_transaction.status = 'held'
        
        # Save to held transactions table
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS held_transactions (
                hold_id TEXT PRIMARY KEY,
                transaction_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                clerk_id TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            INSERT INTO held_transactions VALUES (?, ?, ?, ?)
        ''', (hold_id, json.dumps(asdict(self.current_transaction)),
              datetime.datetime.now().isoformat(),
              self.current_clerk['id'] if self.current_clerk else 'unknown'))
        conn.commit()
        conn.close()
        
        self.current_transaction = None
        return hold_id
    
    def recall_transaction(self, hold_id: str) -> bool:
        """Recall a held transaction"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT transaction_data FROM held_transactions WHERE hold_id = ?', (hold_id,))
        row = cursor.fetchone()
        
        if row:
            data = json.loads(row[0])
            # Restore transaction (simplified - would need full reconstruction)
            cursor.execute('DELETE FROM held_transactions WHERE hold_id = ?', (hold_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def split_check(self, num_splits: int) -> List[float]:
        """Split current transaction into multiple checks"""
        if not self.current_transaction:
            return []
        
        total = self.current_transaction.total
        base_amount = total / num_splits
        splits = []
        
        for i in range(num_splits):
            if i == num_splits - 1:
                # Last split gets any rounding remainder
                split_amount = round(total - sum(splits), 2)
            else:
                split_amount = round(base_amount, 2)
            splits.append(split_amount)
        
        return splits
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount between currencies"""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target
        usd_amount = amount / Config.EXCHANGE_RATES.get(from_currency, 1.0)
        target_amount = usd_amount * Config.EXCHANGE_RATES.get(to_currency, 1.0)
        
        return round(target_amount, 8 if to_currency == 'BTC' else 2)
    
    def generate_payment_qr(self, amount: float, method: str = 'BTC') -> Optional[str]:
        """Generate QR code for payment"""
        if not QR_AVAILABLE:
            return None
        
        if method == 'BTC':
            # Bitcoin payment URI
            btc_amount = self.convert_currency(amount, 'USD', 'BTC')
            qr_data = f"bitcoin:1PerformanceSupplyDepot?amount={btc_amount}&message=Payment"
        else:
            # Generic payment data
            qr_data = f"PAYMENT|{Config.STORE_NAME}|{amount}|{method}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    def update_exchange_rates(self):
        """Fetch latest exchange rates from API"""
        try:
            # Using exchangerate-api.com (free tier available)
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                rates = data.get('rates', {})
                
                # Update Config rates
                Config.EXCHANGE_RATES['EUR'] = rates.get('EUR', 0.85)
                Config.EXCHANGE_RATES['GBP'] = rates.get('GBP', 0.75)
                Config.EXCHANGE_RATES['JPY'] = rates.get('JPY', 110.0)
                Config.EXCHANGE_RATES['CAD'] = rates.get('CAD', 1.25)
                Config.EXCHANGE_RATES['AUD'] = rates.get('AUD', 1.35)
                
                return True
        except (urllib.error.URLError, json.JSONDecodeError, KeyError):
            # Fallback to default rates
            return False


# ==================== GUI APPLICATION ====================

class ReggieStarrGUI:
    def __init__(self, master):
        self.master = master
        master.title(f"ReggieStarr v4.2 - {Config.STORE_NAME}")
        master.geometry("1024x768")
        master.configure(bg='#1a1a2e')
        
        self.register = CashRegister()
        self.input_buffer = ""
        self.last_function = None
        
        self.create_styles()
        self.create_header()
        self.create_display()
        self.create_function_buttons()
        self.create_keypad()
        self.create_payment_buttons()
        
        # Show login dialog
        self.show_login_dialog()
    
    def create_styles(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#1a1a2e')
        self.style.configure('Header.TLabel', background='#16213e', foreground='white', 
                           font=('Courier', 12, 'bold'))
        self.style.configure('Display.TLabel', background='#000000', foreground='#00FF00',
                           font=('Courier', 14))
    
    def create_header(self):
        header = ttk.Frame(self.master, style='TFrame')
        header.pack(fill='x', padx=5, pady=5)
        
        self.lbl_mode = ttk.Label(header, text="MODE: REGISTER", style='Header.TLabel')
        self.lbl_mode.pack(side='left', padx=10)
        
        self.lbl_clerk = ttk.Label(header, text="CLERK: Not Logged In", style='Header.TLabel')
        self.lbl_clerk.pack(side='left', padx=10)
        
        self.lbl_time = ttk.Label(header, text="", style='Header.TLabel')
        self.lbl_time.pack(side='right', padx=10)
        self.update_clock()
    
    def update_clock(self):
        self.lbl_time.config(text=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.master.after(1000, self.update_clock)
    
    def create_display(self):
        display_frame = ttk.Frame(self.master, style='TFrame')
        display_frame.pack(fill='x', padx=10, pady=5)
        
        self.txt_display = scrolledtext.ScrolledText(
            display_frame, height=15, width=80, font=('Courier', 12),
            bg='#000000', fg='#00FF00', insertbackground='#00FF00'
        )
        self.txt_display.pack(fill='both', expand=True)
        self.update_display()
    
    def create_function_buttons(self):
        func_frame = ttk.Frame(self.master, style='TFrame')
        func_frame.pack(fill='x', padx=10, pady=5)
        
        functions = [
            ('PLU', '#4a4a6a'), ('QTY', '#4a4a6a'), ('Price Inquiry', '#4a4a6a'),
            ('Discount', '#6a4a4a'), ('Void Item', '#6a4a4a'), ('Void Txn', '#6a4a4a'),
            ('Subtotal', '#4a6a4a'), ('Total', '#2a6a2a'), ('No Sale', '#4a4a6a'),
            ('Bag Fee', '#4a4a6a'), ('CRV', '#4a4a6a'), ('Tax Exempt', '#4a4a6a'),
            ('Add PLU', '#6a4a6a'), ('Dept Mgmt', '#6a4a6a'), ('Inventory', '#6a4a6a'),
            ('Hold', '#4a6a6a'), ('Recall', '#6a6a4a'), ('Split', '#6a4a6a'),
            ('Currency', '#4a4a8a'), ('QR Pay', '#8a4a8a'), ('Update Rates', '#4a8a4a'),
            ('Layaway', '#6a6a6a'), ('Gift Card', '#8a6a4a'), ('Customer', '#4a6a8a'),
            ('Mode', '#6a4a8a'), ('Reports', '#4a8a6a'), ('Z-Report', '#8a6a6a'),
        ]
        
        for i, (text, color) in enumerate(functions):
            btn = tk.Button(func_frame, text=text, bg=color, fg='white',
                          font=('Arial', 10, 'bold'), width=12, height=2,
                          command=lambda t=text: self.handle_function(t))
            btn.grid(row=i//4, column=i%4, padx=3, pady=3, sticky='nsew')
    
    def create_keypad(self):
        keypad_frame = ttk.Frame(self.master, style='TFrame')
        keypad_frame.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        
        keys = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['C', '0', '00'],
        ]
        
        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                btn = tk.Button(keypad_frame, text=key, bg='#666666', fg='white',
                              font=('Arial', 16, 'bold'), width=8, height=3,
                              command=lambda k=key: self.handle_keypad(k))
                btn.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky='nsew')
        
        # Enter button
        btn_enter = tk.Button(keypad_frame, text='ENTER', bg='#0066CC', fg='white',
                             font=('Arial', 16, 'bold'), width=8, height=3,
                             command=self.handle_enter)
        btn_enter.grid(row=4, column=0, columnspan=3, padx=3, pady=3, sticky='nsew')
    
    def create_payment_buttons(self):
        payment_frame = ttk.Frame(self.master, style='TFrame')
        payment_frame.pack(side='right', fill='y', padx=10, pady=5)
        
        ttk.Label(payment_frame, text="PAYMENT", style='Header.TLabel').pack(pady=5)
        
        for method in Config.PAYMENT_METHODS[:6]:  # Show first 6
            btn = tk.Button(payment_frame, text=method, bg='#2a6a2a', fg='white',
                          font=('Arial', 12), width=15, height=2,
                          command=lambda m=method: self.handle_payment(m))
            btn.pack(pady=2, fill='x')
    
    def show_login_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Clerk Login")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Clerk ID:").pack(pady=5)
        entry_id = ttk.Entry(dialog)
        entry_id.pack(pady=5)
        entry_id.insert(0, "001")
        
        ttk.Label(dialog, text="PIN:").pack(pady=5)
        entry_pin = ttk.Entry(dialog, show="*")
        entry_pin.pack(pady=5)
        entry_pin.insert(0, "1234")
        
        def do_login():
            if self.register.login_clerk(entry_id.get(), entry_pin.get()):
                self.lbl_clerk.config(text=f"CLERK: {self.register.current_clerk['name']}")
                self.register.start_transaction()
                dialog.destroy()
                self.update_display()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        
        ttk.Button(dialog, text="Login", command=do_login).pack(pady=10)
        entry_pin.bind('<Return>', lambda e: do_login())
        entry_id.focus()
    
    def handle_keypad(self, key):
        if key == 'C':
            self.input_buffer = ""
        else:
            self.input_buffer += key
        self.update_display()
    
    def handle_enter(self):
        if self.input_buffer and self.register.current_transaction:
            # Try to add as PLU
            success, msg = self.register.add_item(self.input_buffer, 1)
            if success:
                self.input_buffer = ""
            else:
                messagebox.showerror("Error", msg)
        self.update_display()
    
    def handle_function(self, func):
        if func == "Price Inquiry":
            if self.input_buffer:
                result = self.register.functions['Price Inquiry'](self.input_buffer)
                messagebox.showinfo("Price Inquiry", result)
        elif func == "Void Item":
            if self.input_buffer:
                try:
                    idx = int(self.input_buffer) - 1
                    if self.register.void_item(idx):
                        self.input_buffer = ""
                except ValueError:
                    pass
        elif func == "Void Txn":
            if messagebox.askyesno("Confirm", "Void entire transaction?"):
                self.register.current_transaction = None
                self.register.start_transaction()
                self.input_buffer = ""
        elif func == "Subtotal":
            pass
        elif func == "Total":
            pass
        elif func == "No Sale":
            result = self.register.functions['No Sale']()
            messagebox.showinfo("No Sale", result)
        elif func == "Add PLU":
            self.show_add_plu_dialog()
        elif func == "Dept Mgmt":
            self.show_department_dialog()
        elif func == "Inventory":
            self.show_inventory_dialog()
        elif func == "Hold":
            hold_id = self.register.hold_transaction()
            if hold_id:
                messagebox.showinfo("Transaction Held", f"Hold ID: {hold_id}")
                self.register.start_transaction()
            self.update_display()
        elif func == "Recall":
            self.show_recall_dialog()
        elif func == "Split":
            self.show_split_dialog()
        elif func == "Currency":
            self.show_currency_dialog()
        elif func == "QR Pay":
            self.show_qr_dialog()
        elif func == "Update Rates":
            success = self.register.update_exchange_rates()
            if success:
                messagebox.showinfo("Success", "Exchange rates updated!")
            else:
                messagebox.showwarning("Warning", "Using default rates (API unavailable)")
        elif func == "Layaway":
            self.show_layaway_dialog()
        elif func == "Gift Card":
            self.show_gift_card_dialog()
        elif func == "Customer":
            self.show_customer_dialog()
        elif func == "Mode":
            self.show_mode_dialog()
        elif func == "Reports":
            self.show_reports_dialog()
        elif func == "Z-Report":
            self.generate_z_report()
        
        self.update_display()

    def generate_z_report(self):
        """Generate and print Z-Report (End of Day)"""
        report = self.register.generate_z_report()

        # Show in dialog
        dialog = tk.Toplevel(self.master)
        dialog.title("Z-Report (End of Day)")
        dialog.geometry("500x600")
        dialog.transient(self.master)

        text = scrolledtext.ScrolledText(dialog, height=30, width=60, font=('Courier', 10))
        text.pack(padx=10, pady=10, fill='both', expand=True)
        text.insert('1.0', report)

        # Save button
        def save_and_close():
            filename = f"zreport_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
            self.save_report(filename, report)
            dialog.destroy()

        ttk.Button(dialog, text="Save & Close", command=save_and_close).pack(pady=10)
        ttk.Button(dialog, text="Print (Simulated)",
                  command=lambda: messagebox.showinfo("Print", "Sending to printer...")).pack(pady=5)
    
    def show_layaway_dialog(self):
        """Dialog for layaway management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Layaway Management")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Create Layaway
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Create Layaway")
        
        if not self.register.current_transaction or self.register.current_transaction.total <= 0:
            ttk.Label(tab1, text="No active transaction to put on layaway.").pack(pady=20)
        else:
            ttk.Label(tab1, text=f"Total Amount: ${self.register.current_transaction.total:.2f}").pack(pady=10)
            
            ttk.Label(tab1, text="Customer ID:").pack(pady=5)
            cust_entry = ttk.Entry(tab1, width=20)
            cust_entry.pack(pady=5)
            
            ttk.Label(tab1, text="Deposit Amount:").pack(pady=5)
            deposit_entry = ttk.Entry(tab1, width=15)
            deposit_entry.insert(0, f"{self.register.current_transaction.total * 0.25:.2f}")
            deposit_entry.pack(pady=5)
            
            ttk.Label(tab1, text="Due Date (YYYY-MM-DD):").pack(pady=5)
            due_entry = ttk.Entry(tab1, width=15)
            due_entry.insert(0, (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d'))
            due_entry.pack(pady=5)
            
            def create_layaway():
                try:
                    deposit = float(deposit_entry.get())
                    due_date = datetime.datetime.strptime(due_entry.get(), '%Y-%m-%d')
                    customer_id = cust_entry.get().strip() or "WALKIN"
                    
                    layaway_id = self.register.create_layaway(deposit, customer_id, due_date)
                    messagebox.showinfo("Success", f"Layaway created: {layaway_id}")
                    dialog.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid input: {e}")
            
            ttk.Button(tab1, text="Create Layaway", command=create_layaway).pack(pady=20)
        
        # Tab 2: Make Payment
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Make Payment")
        
        ttk.Label(tab2, text="Layaway ID:").grid(row=0, column=0, padx=5, pady=5)
        layaway_entry = ttk.Entry(tab2, width=20)
        layaway_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(tab2, text="Payment Amount:").grid(row=1, column=0, padx=5, pady=5)
        payment_entry = ttk.Entry(tab2, width=15)
        payment_entry.grid(row=1, column=1, padx=5, pady=5)
        
        result_label = ttk.Label(tab2, text="", font=('Courier', 12))
        result_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        def make_payment():
            try:
                layaway_id = layaway_entry.get().strip()
                amount = float(payment_entry.get())
                success, new_balance = self.register.process_layaway_payment(layaway_id, amount)
                if success:
                    result_label.config(text=f"Payment accepted. New balance: ${new_balance:.2f}")
                else:
                    messagebox.showerror("Error", "Layaway not found or payment failed")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(tab2, text="Process Payment", command=make_payment).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_gift_card_dialog(self):
        """Dialog for gift card management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Gift Card Management")
        dialog.geometry("400x400")
        dialog.transient(self.master)
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Issue Card
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Issue Card")
        
        ttk.Label(tab1, text="Card ID:").grid(row=0, column=0, padx=5, pady=5)
        card_entry = ttk.Entry(tab1, width=20)
        card_entry.grid(row=0, column=1, padx=5, pady=5)
        card_entry.insert(0, f"GC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        ttk.Label(tab1, text="Initial Amount:").grid(row=1, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(tab1, width=15)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        amount_entry.insert(0, "50.00")
        
        def issue_card():
            try:
                card_id = card_entry.get().strip()
                amount = float(amount_entry.get())
                if self.register.issue_gift_card(card_id, amount):
                    messagebox.showinfo("Success", f"Gift card {card_id} issued with ${amount:.2f}")
                    dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(tab1, text="Issue Card", command=issue_card).grid(row=2, column=0, columnspan=2, pady=20)
        
        # Tab 2: Check Balance
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Check Balance")
        
        ttk.Label(tab2, text="Card ID:").grid(row=0, column=0, padx=5, pady=5)
        check_entry = ttk.Entry(tab2, width=20)
        check_entry.grid(row=0, column=1, padx=5, pady=5)
        
        balance_label = ttk.Label(tab2, text="", font=('Courier', 16, 'bold'))
        balance_label.grid(row=1, column=0, columnspan=2, pady=20)
        
        def check_balance():
            card_id = check_entry.get().strip()
            balance = self.register.get_gift_card_balance(card_id)
            balance_label.config(text=f"Balance: ${balance:.2f}")
        
        ttk.Button(tab2, text="Check", command=check_balance).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Tab 3: Redeem
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Redeem")
        
        ttk.Label(tab3, text="Card ID:").grid(row=0, column=0, padx=5, pady=5)
        redeem_card_entry = ttk.Entry(tab3, width=20)
        redeem_card_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(tab3, text="Amount to Redeem:").grid(row=1, column=0, padx=5, pady=5)
        redeem_amount_entry = ttk.Entry(tab3, width=15)
        redeem_amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def redeem():
            try:
                card_id = redeem_card_entry.get().strip()
                amount = float(redeem_amount_entry.get())
                if self.register.redeem_gift_card(card_id, amount):
                    messagebox.showinfo("Success", f"Redeemed ${amount:.2f} from card {card_id}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Insufficient balance or invalid card")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(tab3, text="Redeem", command=redeem).grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_customer_dialog(self):
        """Dialog for customer management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Customer Management")
        dialog.geometry("500x500")
        dialog.transient(self.master)
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Add Customer
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Add Customer")
        
        fields = [
            ("Customer ID:", "cust_id", f"CUST-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"),
            ("Name:", "name", ""),
            ("Email:", "email", ""),
            ("Phone:", "phone", ""),
        ]
        
        entries = {}
        for i, (label, key, default) in enumerate(fields):
            ttk.Label(tab1, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(tab1, width=25)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, default)
            entries[key] = entry
        
        def add_customer():
            customer_id = entries['cust_id'].get().strip()
            name = entries['name'].get().strip()
            email = entries['email'].get().strip()
            phone = entries['phone'].get().strip()
            
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            
            if self.register.add_customer(customer_id, name, email, phone):
                messagebox.showinfo("Success", f"Customer {name} added")
                dialog.destroy()
        
        ttk.Button(tab1, text="Add Customer", command=add_customer).grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        # Tab 2: Lookup Customer
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Lookup")
        
        ttk.Label(tab2, text="Customer ID:").grid(row=0, column=0, padx=5, pady=5)
        lookup_entry = ttk.Entry(tab2, width=20)
        lookup_entry.grid(row=0, column=1, padx=5, pady=5)
        
        info_text = scrolledtext.ScrolledText(tab2, height=15, width=50)
        info_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        def lookup():
            customer_id = lookup_entry.get().strip()
            customer = self.register.get_customer(customer_id)
            info_text.delete('1.0', tk.END)
            if customer:
                info_text.insert(tk.END, f"Customer ID: {customer['customer_id']}\n")
                info_text.insert(tk.END, f"Name: {customer['name']}\n")
                info_text.insert(tk.END, f"Email: {customer['email']}\n")
                info_text.insert(tk.END, f"Phone: {customer['phone']}\n")
                info_text.insert(tk.END, f"Total Purchases: ${customer['total_purchases']:.2f}\n")
                info_text.insert(tk.END, f"Visit Count: {customer['visit_count']}\n")
            else:
                info_text.insert(tk.END, "Customer not found")
        
        ttk.Button(tab2, text="Lookup", command=lookup).grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_recall_dialog(self):
        """Dialog to recall held transactions"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Recall Held Transaction")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Enter Hold ID:").pack(pady=10)
        entry = ttk.Entry(dialog, width=20)
        entry.pack(pady=5)
        
        def recall():
            hold_id = entry.get().strip()
            if self.register.recall_transaction(hold_id):
                messagebox.showinfo("Success", f"Recalled transaction {hold_id}")
                dialog.destroy()
                self.update_display()
            else:
                messagebox.showerror("Error", "Hold ID not found")
        
        ttk.Button(dialog, text="Recall", command=recall).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)
    
    def show_split_dialog(self):
        """Dialog to split check"""
        if not self.register.current_transaction:
            messagebox.showerror("Error", "No active transaction")
            return
        
        dialog = tk.Toplevel(self.master)
        dialog.title("Split Check")
        dialog.geometry("400x400")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text=f"Total: ${self.register.current_transaction.total:.2f}").pack(pady=10)
        ttk.Label(dialog, text="Number of splits:").pack(pady=5)
        
        spinbox = tk.Spinbox(dialog, from_=2, to=10, width=10)
        spinbox.pack(pady=5)
        
        result_text = scrolledtext.ScrolledText(dialog, height=10, width=40)
        result_text.pack(pady=10, padx=10)
        
        def calculate_splits():
            try:
                num = int(spinbox.get())
                splits = self.register.split_check(num)
                result_text.delete('1.0', tk.END)
                for i, amount in enumerate(splits, 1):
                    result_text.insert(tk.END, f"Check {i}: ${amount:.2f}\n")
            except ValueError:
                messagebox.showerror("Error", "Invalid number")
        
        ttk.Button(dialog, text="Calculate", command=calculate_splits).pack(pady=5)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)

    def show_mode_dialog(self):
        """Dialog to change TEC MA-79 mode"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Select Mode")
        dialog.geometry("400x300")
        dialog.transient(self.master)

        ttk.Label(dialog, text="Current Mode: " + self.register.mode, font=('Courier', 14, 'bold')).pack(pady=10)

        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(pady=20)

        for mode, description in Config.MODES.items():
            btn = tk.Button(mode_frame, text=mode, width=15,
                          bg='#4a4a6a' if mode != self.register.mode else '#2a6a2a',
                          fg='white', font=('Arial', 12),
                          command=lambda m=mode: self.change_mode(m, dialog))
            btn.pack(pady=5)
            ttk.Label(mode_frame, text=description, font=('Arial', 9)).pack()

    def change_mode(self, mode, dialog):
        if self.register.set_mode(mode):
            self.lbl_mode.config(text=f"MODE: {mode}")
            dialog.destroy()
            self.update_display()

    def show_reports_dialog(self):
        """Dialog for comprehensive reporting"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Reports")
        dialog.geometry("600x500")
        dialog.transient(self.master)

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Group Report
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Group/Dept")

        text1 = scrolledtext.ScrolledText(tab1, height=20, width=70)
        text1.pack(padx=10, pady=10, fill='both', expand=True)
        text1.insert('1.0', self.register.generate_group_report())

        ttk.Button(tab1, text="Save to File",
                  command=lambda: self.save_report("group_report.txt", text1.get('1.0', tk.END))).pack(pady=5)

        # Tab 2: PLU Report
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="PLU")

        text2 = scrolledtext.ScrolledText(tab2, height=20, width=70)
        text2.pack(padx=10, pady=10, fill='both', expand=True)
        text2.insert('1.0', self.register.generate_plu_report())

        ttk.Button(tab2, text="Save to File",
                  command=lambda: self.save_report("plu_report.txt", text2.get('1.0', tk.END))).pack(pady=5)

        # Tab 3: Period Report
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Period")

        period_var = tk.StringVar(value='hourly')
        ttk.Radiobutton(tab3, text="Hourly", variable=period_var, value='hourly').pack()
        ttk.Radiobutton(tab3, text="Daily", variable=period_var, value='daily').pack()
        ttk.Radiobutton(tab3, text="Weekly", variable=period_var, value='weekly').pack()
        ttk.Radiobutton(tab3, text="Monthly", variable=period_var, value='monthly').pack()

        text3 = scrolledtext.ScrolledText(tab3, height=15, width=70)
        text3.pack(padx=10, pady=10, fill='both', expand=True)

        def generate_period():
            text3.delete('1.0', tk.END)
            text3.insert('1.0', self.register.generate_period_report(period_var.get()))

        ttk.Button(tab3, text="Generate", command=generate_period).pack(pady=5)
        ttk.Button(tab3, text="Save to File",
                  command=lambda: self.save_report(f"period_{period_var.get()}_report.txt", text3.get('1.0', tk.END))).pack(pady=5)

        # Tab 4: Sales Totals
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Sales Totals")

        text4 = scrolledtext.ScrolledText(tab4, height=20, width=70)
        text4.pack(padx=10, pady=10, fill='both', expand=True)
        text4.insert('1.0', self.register.generate_sales_totals())

        ttk.Button(tab4, text="Refresh",
                  command=lambda: text4.insert('1.0', self.register.generate_sales_totals())).pack(pady=5)
        ttk.Button(tab4, text="Save to File",
                  command=lambda: self.save_report("sales_totals.txt", text4.get('1.0', tk.END))).pack(pady=5)

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def save_report(self, filename, content):
        """Save report to file"""
        try:
            with open(filename, 'w') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Report saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save report: {e}")

    def show_currency_dialog(self):
        """Dialog for currency conversion"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Currency Conversion")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(dialog, width=15)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)
        amount_entry.insert(0, "100.00")
        
        ttk.Label(dialog, text="From:").grid(row=1, column=0, padx=5, pady=5)
        from_var = tk.StringVar(value="USD")
        from_menu = ttk.Combobox(dialog, textvariable=from_var, values=list(Config.EXCHANGE_RATES.keys()), width=10)
        from_menu.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="To:").grid(row=2, column=0, padx=5, pady=5)
        to_var = tk.StringVar(value="EUR")
        to_menu = ttk.Combobox(dialog, textvariable=to_var, values=list(Config.EXCHANGE_RATES.keys()), width=10)
        to_menu.grid(row=2, column=1, padx=5, pady=5)
        
        result_label = ttk.Label(dialog, text="", font=('Courier', 14, 'bold'))
        result_label.grid(row=3, column=0, columnspan=2, pady=20)
        
        def convert():
            try:
                amount = float(amount_entry.get())
                from_curr = from_var.get()
                to_curr = to_var.get()
                result = self.register.convert_currency(amount, from_curr, to_curr)
                symbol = Config.CURRENCY_SYMBOLS.get(to_curr, '$')
                result_label.config(text=f"{symbol}{result:,.2f}" if to_curr != 'BTC' else f"₿{result:.8f}")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(dialog, text="Convert", command=convert).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Show current rates
        rates_text = "Current Rates (USD base):\n"
        for curr, rate in list(Config.EXCHANGE_RATES.items())[:5]:
            rates_text += f"  {curr}: {rate}\n"
        ttk.Label(dialog, text=rates_text, justify='left').grid(row=5, column=0, columnspan=2, pady=10)
    
    def show_qr_dialog(self):
        """Dialog for QR code payment"""
        if not QR_AVAILABLE:
            messagebox.showwarning("Not Available", "QR code support requires 'qrcode' and 'PIL' packages")
            return
        
        if not self.register.current_transaction:
            messagebox.showerror("Error", "No active transaction")
            return
        
        dialog = tk.Toplevel(self.master)
        dialog.title("QR Code Payment")
        dialog.geometry("400x500")
        dialog.transient(self.master)
        
        amount = self.register.current_transaction.total
        ttk.Label(dialog, text=f"Amount: ${amount:.2f}").pack(pady=10)
        
        method_var = tk.StringVar(value="BTC")
        ttk.Radiobutton(dialog, text="Bitcoin (BTC)", variable=method_var, value="BTC").pack()
        ttk.Radiobutton(dialog, text="Other", variable=method_var, value="OTHER").pack()
        
        qr_label = ttk.Label(dialog)
        qr_label.pack(pady=20)
        
        def generate():
            img = self.register.generate_payment_qr(amount, method_var.get())
            if img:
                # Convert PIL image for Tkinter
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img)
                qr_label.config(image=photo)
                qr_label.image = photo  # Keep reference
        
        ttk.Button(dialog, text="Generate QR", command=generate).pack(pady=10)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_add_plu_dialog(self):
        """Dialog for adding new PLU/product"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Add New PLU")
        dialog.geometry("400x500")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Form fields
        fields = [
            ("PLU Code:", "code"),
            ("Product Name:", "name"),
            ("Price:", "price"),
            ("Initial Quantity:", "quantity"),
            ("Department:", "department"),
            ("PLU Code (optional):", "plu"),
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=25)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry
        
        # Tax rates checkboxes
        ttk.Label(dialog, text="Tax Rates:").grid(row=len(fields), column=0, padx=5, pady=5, sticky='ne')
        tax_frame = ttk.Frame(dialog)
        tax_frame.grid(row=len(fields), column=1, padx=5, pady=5, sticky='w')
        
        tax_vars = {}
        for i, (tax_name, rate) in enumerate(Config.TAX_RATES.items()):
            var = tk.BooleanVar(value=(tax_name == 'Berkeley'))
            tax_vars[tax_name] = var
            ttk.Checkbutton(tax_frame, text=f"{tax_name} ({rate:.2%})", variable=var).grid(row=i, column=0, sticky='w')
        
        # CRV checkbox
        crv_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="CRV Applicable", variable=crv_var).grid(row=len(fields)+1, column=1, sticky='w', padx=5)
        
        # Open price checkbox
        open_price_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Allow Price Override", variable=open_price_var).grid(row=len(fields)+2, column=1, sticky='w', padx=5)
        
        def save_plu():
            try:
                code = entries['code'].get().strip()
                name = entries['name'].get().strip()
                price = float(entries['price'].get())
                quantity = int(entries['quantity'].get())
                department = entries['department'].get().strip() or "General"
                plu_code = entries['plu'].get().strip() or None
                
                selected_taxes = [tax for tax, var in tax_vars.items() if var.get()]
                
                product = Product(
                    code=code,
                    name=name,
                    price=price,
                    quantity=quantity,
                    department=department,
                    tax_rates=selected_taxes,
                    track_inventory=True,
                    open_price=open_price_var.get(),
                    plu_code=plu_code,
                    crv_applicable=crv_var.get(),
                    crv_rate=0.05 if crv_var.get() else 0.0
                )
                
                self.register.add_product(product)
                messagebox.showinfo("Success", f"Added PLU: {name}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
        
        ttk.Button(dialog, text="Save PLU", command=save_plu).grid(row=len(fields)+3, column=0, columnspan=2, pady=20)
    
    def show_department_dialog(self):
        """Dialog for department management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Department Management")
        dialog.geometry("600x500")
        dialog.transient(self.master)
        
        # Get unique departments
        departments = {}
        for product in self.register.products.values():
            dept = product.department
            if dept not in departments:
                departments[dept] = {'products': [], 'total_value': 0}
            departments[dept]['products'].append(product)
            departments[dept]['total_value'] += product.price * product.quantity
        
        # Treeview for departments
        tree = ttk.Treeview(dialog, columns=('Products', 'Total Value'), show='tree headings')
        tree.heading('#0', text='Department')
        tree.heading('Products', text='Products')
        tree.heading('Total Value', text='Inventory Value')
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        for dept_name, data in sorted(departments.items()):
            item_count = len(data['products'])
            value = data['total_value']
            tree.insert('', 'end', text=dept_name, values=(item_count, f"${value:.2f}"))
        
        # Assign product to department section
        ttk.Label(dialog, text="Reassign Product to Department:").pack(pady=(10, 5))
        
        assign_frame = ttk.Frame(dialog)
        assign_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(assign_frame, text="Product Code:").grid(row=0, column=0, padx=5)
        product_entry = ttk.Entry(assign_frame, width=15)
        product_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(assign_frame, text="New Department:").grid(row=0, column=2, padx=5)
        dept_entry = ttk.Entry(assign_frame, width=20)
        dept_entry.grid(row=0, column=3, padx=5)
        
        def assign_department():
            code = product_entry.get().strip()
            new_dept = dept_entry.get().strip()
            
            if code in self.register.products:
                product = self.register.products[code]
                product.department = new_dept
                self.register.add_product(product)
                messagebox.showinfo("Success", f"Assigned {product.name} to {new_dept}")
                dialog.destroy()
                self.show_department_dialog()  # Refresh
            else:
                messagebox.showerror("Error", "Product not found")
        
        ttk.Button(assign_frame, text="Assign", command=assign_department).grid(row=0, column=4, padx=5)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def show_inventory_dialog(self):
        """Dialog for inventory management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Inventory Management")
        dialog.geometry("800x600")
        dialog.transient(self.master)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: All Products
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="All Products")
        
        # Treeview for products
        columns = ('Code', 'Name', 'Price', 'Stock', 'Department', 'Status')
        tree = ttk.Treeview(tab1, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab1, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate tree
        for code, product in sorted(self.register.products.items()):
            status = "LOW" if product.quantity < 10 else "OK" if product.quantity > 0 else "OUT"
            tree.insert('', 'end', values=(
                code, product.name, f"${product.price:.2f}",
                product.quantity, product.department, status
            ))
        
        # Tab 2: Low Stock
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Low Stock Alerts")
        
        low_stock_tree = ttk.Treeview(tab2, columns=columns[:5], show='headings')
        for col in columns[:5]:
            low_stock_tree.heading(col, text=col)
            low_stock_tree.column(col, width=120)
        low_stock_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        for code, product in sorted(self.register.products.items()):
            if product.quantity < 10:
                low_stock_tree.insert('', 'end', values=(
                    code, product.name, f"${product.price:.2f}",
                    product.quantity, product.department
                ))
        
        # Tab 3: Stock Adjustment
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Adjust Stock")
        
        ttk.Label(tab3, text="Product Code:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        code_entry = ttk.Entry(tab3, width=20)
        code_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(tab3, text="Adjustment (+/-):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        adj_entry = ttk.Entry(tab3, width=20)
        adj_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(tab3, text="Reason:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        reason_entry = ttk.Entry(tab3, width=30)
        reason_entry.grid(row=2, column=1, padx=5, pady=5)
        reason_entry.insert(0, "Stock adjustment")
        
        def adjust_stock():
            try:
                code = code_entry.get().strip()
                adjustment = int(adj_entry.get())
                reason = reason_entry.get().strip()
                
                if code in self.register.products:
                    product = self.register.products[code]
                    new_qty = product.quantity + adjustment
                    if new_qty < 0:
                        messagebox.showerror("Error", "Cannot reduce stock below 0")
                        return
                    
                    product.quantity = new_qty
                    self.register.add_product(product)
                    
                    # Log adjustment
                    conn = self.register.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO inventory_log (product_code, adjustment, reason, new_quantity, timestamp, clerk_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (code, adjustment, reason, new_qty, datetime.datetime.now().isoformat(),
                          self.register.current_clerk['id'] if self.register.current_clerk else 'system'))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", f"Stock adjusted. New quantity: {new_qty}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Product not found")
            except ValueError:
                messagebox.showerror("Error", "Invalid adjustment amount")
        
        ttk.Button(tab3, text="Adjust Stock", command=adjust_stock).grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def handle_payment(self, method):
        if not self.register.current_transaction:
            return
        
        remaining = self.register.current_transaction.total - sum(
            p['amount'] for p in self.register.current_transaction.payments
        )
        
        if remaining <= 0:
            return
        
        if method == "Cash":
            dialog = tk.Toplevel(self.master)
            dialog.title("Cash Payment")
            dialog.transient(self.master)
            
            ttk.Label(dialog, text=f"Total: {Config.CURRENCY_SYMBOL}{remaining:.2f}").pack(pady=5)
            ttk.Label(dialog, text="Amount Tendered:").pack(pady=5)
            entry_amount = ttk.Entry(dialog)
            entry_amount.pack(pady=5)
            entry_amount.insert(0, f"{remaining:.2f}")
            
            def process():
                try:
                    amount = float(entry_amount.get())
                    success, rem = self.register.add_payment(method, amount)
                    if success and rem <= 0:
                        messagebox.showinfo("Complete", f"Change: {Config.CURRENCY_SYMBOL}{self.register.current_transaction.change:.2f}")
                        self.register.current_transaction = None
                        self.register.start_transaction()
                    dialog.destroy()
                    self.update_display()
                except ValueError:
                    messagebox.showerror("Error", "Invalid amount")
            
            ttk.Button(dialog, text="Process", command=process).pack(pady=10)
            entry_amount.bind('<Return>', lambda e: process())
            entry_amount.focus()
        else:
            success, rem = self.register.add_payment(method, remaining)
            if success and rem <= 0:
                messagebox.showinfo("Complete", "Transaction complete!")
                self.register.current_transaction = None
                self.register.start_transaction()
            self.update_display()
    
    def update_display(self):
        text = f"{Config.STORE_NAME}\n"
        text += f"Mode: {self.register.mode} | Clerk: {self.register.current_clerk['name'] if self.register.current_clerk else 'None'}\n"
        text += "=" * 50 + "\n\n"
        
        if self.register.current_transaction:
            for i, item in enumerate(self.register.current_transaction.items, 1):
                if not item.voided:
                    text += f"{i:2d}. {item.name[:20]:20s} x{item.quantity:4.1f} {Config.CURRENCY_SYMBOL}{item.total:8.2f}\n"
            
            text += "\n" + "=" * 50 + "\n"
            text += f"Subtotal: {Config.CURRENCY_SYMBOL}{self.register.current_transaction.subtotal:10.2f}\n"
            text += f"Tax:      {Config.CURRENCY_SYMBOL}{self.register.current_transaction.tax_total:10.2f}\n"
            if self.register.current_transaction.crv_total > 0:
                text += f"CRV:      {Config.CURRENCY_SYMBOL}{self.register.current_transaction.crv_total:10.2f}\n"
            text += f"TOTAL:    {Config.CURRENCY_SYMBOL}{self.register.current_transaction.total:10.2f}\n"
            
            total_paid = sum(p['amount'] for p in self.register.current_transaction.payments)
            if total_paid > 0:
                text += f"Paid:     {Config.CURRENCY_SYMBOL}{total_paid:10.2f}\n"
                remaining = self.register.current_transaction.total - total_paid
                if remaining > 0:
                    text += f"Due:      {Config.CURRENCY_SYMBOL}{remaining:10.2f}\n"
        else:
            text += "No active transaction\n"
        
        if self.input_buffer:
            text += f"\nInput: {self.input_buffer}"
        
        self.txt_display.delete('1.0', tk.END)
        self.txt_display.insert('1.0', text)
        self.txt_display.see(tk.END)


# ==================== MAIN ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = ReggieStarrGUI(root)
    root.mainloop()
