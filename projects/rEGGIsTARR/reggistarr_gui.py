#!/usr/bin/env python3
"""
rEGGIsTARR GUI - Full Tkinter Interface for TEC MA-79 Digital Cash Register
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
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

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
    def no_sale(self): return "Drawer opened"
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


# ==================== GUI APPLICATION ====================

class ReggieStarrGUI:
    def __init__(self, master):
        self.master = master
        master.title(f"rEGGIsTARR v4.1 - {Config.STORE_NAME}")
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
        
        self.update_display()
    
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
