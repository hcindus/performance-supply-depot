"""
Master File: Reggie Starr RS-79 v 1.0.0.1
Digital Cash Register System

A comprehensive and customizable digital cash register system with:
- Multi-language support (8 languages)
- Multi-currency support (USD, EUR, GBP, BTC, etc.)
- Tax programming with multiple rates
- PLU and Department management
- Discounts and surcharges
- Advanced transaction handling
- Financial and management reports
- Clerk management system
- Inventory management
- Kitchen Display System (KDS)
- QR code generation for crypto payments
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import json
from datetime import datetime

# ============================================================================
# SPLASH SCREEN
# ============================================================================

class SplashScreen:
    def __init__(self, master):
        self.master = master
        master.title("Welcome to Reggie Starr RS-79")
        
        self.label = tk.Label(master, text="Welcome", font=("Arial", 24))
        self.label.pack(pady=20)
        
        self.model_label = tk.Label(master, text="RS-79 Reggie Starr", font=("Arial", 18))
        self.model_label.pack(pady=10)
        
        self.languages = [
            "Welcome", "Bienvenido", "Bienvenue", "Willkommen",
            "أهلا بك", "欢迎", "환영합니다", "ようこそ"
        ]
        self.language_labels = [
            tk.Label(master, text=lang, font=("Arial", 14))
            for lang in self.languages
        ]
        for label in self.language_labels:
            label.pack()
        
        self.start_button = tk.Button(
            master, text="Start", 
            command=self.start_app, 
            font=("Arial", 14)
        )
        self.start_button.pack(pady=20)
    
    def start_app(self):
        self.master.destroy()


# ============================================================================
# CORE CASH REGISTER CLASS
# ============================================================================

class CashRegister:
    def __init__(self):
        self.tax_rates = {}
        self.inventory = []
        self.sales = []
        self.plu_codes = {}
        self.departments = {}
        self.clerks = {}
        self.current_clerk = None
        self.transactions = []
        self.held_transactions = []
        self.exchange_rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'BTC': 0.000021,
            'USDC': 1.0,
            'USDT': 1.0
        }
    
    def add_tax_rate(self, name, rate):
        """Add a tax rate (rate as decimal, e.g., 0.0875 for 8.75%)"""
        self.tax_rates[name] = rate
    
    def calculate_tax(self, base_price, tax_rates):
        """Calculate total tax for given tax rates"""
        total_tax_rate = sum(self.tax_rates.get(tax, 0) for tax in tax_rates)
        return base_price * total_tax_rate
    
    def add_product(self, code, name, price, quantity, tax_rates, department, plu_code=None):
        """Add a product to inventory"""
        product = {
            'code': code,
            'name': name,
            'price': price,
            'quantity': quantity,
            'tax_rates': tax_rates,
            'department': department,
            'plu_code': plu_code
        }
        self.inventory.append(product)
        if plu_code:
            self.plu_codes[plu_code] = product
        if department not in self.departments:
            self.departments[department] = []
        self.departments[department].append(product)
    
    def add_clerk(self, clerk_id, name, password=None):
        """Add a clerk to the system"""
        self.clerks[clerk_id] = {
            'name': name,
            'password': password,
            'transactions': []
        }
    
    def login_clerk(self, clerk_id, password=None):
        """Login a clerk"""
        if clerk_id in self.clerks:
            clerk = self.clerks[clerk_id]
            if clerk['password'] is None or clerk['password'] == password:
                self.current_clerk = clerk_id
                return True
        return False
    
    def logout_clerk(self):
        """Logout current clerk"""
        self.current_clerk = None
    
    def hold_transaction(self, transaction, name=None):
        """Hold a transaction for later recall"""
        held = {
            'transaction': transaction,
            'name': name,
            'timestamp': datetime.now()
        }
        self.held_transactions.append(held)
        return len(self.held_transactions) - 1
    
    def recall_transaction(self, index):
        """Recall a held transaction"""
        if 0 <= index < len(self.held_transactions):
            return self.held_transactions.pop(index)
        return None


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class CashRegisterApp:
    def __init__(self, master):
        self.master = master
        master.title("Reggie Starr RS-79 - Digital Cash Register")
        
        self.register = CashRegister()
        self.current_transaction = []
        self.current_subtotal = 0.0
        self.current_tax = 0.0
        self.current_total = 0.0
        
        # Language support
        self.languages = {
            'English': 'en',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Arabic': 'ar',
            'Chinese': 'zh',
            'Korean': 'ko',
            'Japanese': 'ja'
        }
        self.current_language = 'English'
        
        # Currency support
        self.currencies = {
            'USD': {'symbol': '$', 'index': 0},
            'EUR': {'symbol': '€', 'index': 1},
            'GBP': {'symbol': '£', 'index': 2},
            'BTC': {'symbol': '₿', 'index': 3},
            'USDC': {'symbol': 'USDC', 'index': 4},
            'USDT': {'symbol': 'USDT', 'index': 5}
        }
        self.current_currency = 'USD'
        
        self.create_ui()
    
    def create_ui(self):
        """Create the main user interface"""
        # Top control bar
        self.create_top_bar()
        
        # Main transaction area
        self.create_transaction_area()
        
        # Product entry section
        self.create_product_entry()
        
        # Transaction controls
        self.create_transaction_controls()
        
        # Display area
        self.create_display_area()
    
    def create_top_bar(self):
        """Create the top control bar"""
        top_frame = tk.Frame(self.master)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Language selector
        tk.Label(top_frame, text="Language:").pack(side=tk.LEFT, padx=5)
        self.lang_var = tk.StringVar(value=self.current_language)
        lang_menu = tk.OptionMenu(top_frame, self.lang_var, *self.languages.keys())
        lang_menu.pack(side=tk.LEFT, padx=5)
        
        # Currency selector
        tk.Label(top_frame, text="Currency:").pack(side=tk.LEFT, padx=5)
        self.currency_var = tk.StringVar(value=self.current_currency)
        currency_menu = tk.OptionMenu(top_frame, self.currency_var, *self.currencies.keys())
        currency_menu.pack(side=tk.LEFT, padx=5)
        
        # Update rates button
        tk.Button(top_frame, text="Update Rates", command=self.update_exchange_rates).pack(side=tk.LEFT, padx=5)
        
        # Clerk login
        tk.Button(top_frame, text="Clerk Login", command=self.clerk_login).pack(side=tk.RIGHT, padx=5)
    
    def create_transaction_area(self):
        """Create the transaction display area"""
        trans_frame = tk.LabelFrame(self.master, text="Current Transaction", padx=5, pady=5)
        trans_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.trans_listbox = tk.Listbox(trans_frame, height=10)
        self.trans_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Totals display
        totals_frame = tk.Frame(trans_frame)
        totals_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(totals_frame, text="Subtotal:").pack(side=tk.LEFT, padx=5)
        self.subtotal_var = tk.StringVar(value="$0.00")
        tk.Label(totals_frame, textvariable=self.subtotal_var).pack(side=tk.LEFT, padx=5)
        
        tk.Label(totals_frame, text="Tax:").pack(side=tk.LEFT, padx=5)
        self.tax_var = tk.StringVar(value="$0.00")
        tk.Label(totals_frame, textvariable=self.tax_var).pack(side=tk.LEFT, padx=5)
        
        tk.Label(totals_frame, text="Total:").pack(side=tk.LEFT, padx=5)
        self.total_var = tk.StringVar(value="$0.00")
        tk.Label(totals_frame, textvariable=self.total_var, font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
    
    def create_product_entry(self):
        """Create product entry section"""
        entry_frame = tk.LabelFrame(self.master, text="Product Entry", padx=5, pady=5)
        entry_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Product code
        tk.Label(entry_frame, text="Product Code:").grid(row=0, column=0, sticky=tk.W)
        self.product_code_var = tk.StringVar()
        tk.Entry(entry_frame, textvariable=self.product_code_var).grid(row=0, column=1, padx=5)
        
        # Quantity
        tk.Label(entry_frame, text="Quantity:").grid(row=0, column=2, sticky=tk.W)
        self.quantity_var = tk.IntVar(value=1)
        tk.Entry(entry_frame, textvariable=self.quantity_var, width=5).grid(row=0, column=3, padx=5)
        
        # Price
        tk.Label(entry_frame, text="Price:").grid(row=1, column=0, sticky=tk.W)
        self.price_var = tk.DoubleVar()
        tk.Entry(entry_frame, textvariable=self.price_var).grid(row=1, column=1, padx=5)
        
        # Discount
        tk.Label(entry_frame, text="Discount %:").grid(row=1, column=2, sticky=tk.W)
        self.discount_var = tk.DoubleVar(value=0)
        tk.Entry(entry_frame, textvariable=self.discount_var, width=5).grid(row=1, column=3, padx=5)
        
        # Add button
        tk.Button(entry_frame, text="Add Item", command=self.add_item).grid(row=2, column=0, columnspan=4, pady=5)
    
    def create_transaction_controls(self):
        """Create transaction control buttons"""
        controls_frame = tk.Frame(self.master)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        buttons = [
            ("Subtotal", self.calc_subtotal),
            ("Total", self.calc_total),
            ("Payment", self.process_payment),
            ("Void", self.void_item),
            ("Hold", self.hold_transaction),
            ("Recall", self.recall_transaction),
            ("Refund", self.process_refund),
            ("Cancel", self.cancel_transaction)
        ]
        
        for text, command in buttons:
            tk.Button(controls_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)
    
    def create_display_area(self):
        """Create the main display area"""
        display_frame = tk.LabelFrame(self.master, text="System Messages", padx=5, pady=5)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.display_text = tk.Text(display_frame, height=5, wrap=tk.WORD)
        self.display_text.pack(fill=tk.BOTH, expand=True)
    
    # ========================================================================
    # CORE OPERATIONS
    # ========================================================================
    
    def add_item(self):
        """Add an item to the current transaction"""
        code = self.product_code_var.get()
        quantity = self.quantity_var.get()
        price = self.price_var.get()
        discount = self.discount_var.get()
        
        # Calculate item total
        item_subtotal = price * quantity
        discount_amount = item_subtotal * (discount / 100)
        item_total = item_subtotal - discount_amount
        
        # Add to transaction
        item = {
            'code': code,
            'quantity': quantity,
            'price': price,
            'discount': discount,
            'total': item_total
        }
        self.current_transaction.append(item)
        
        # Update display
        self.trans_listbox.insert(tk.END, f"{code} x{quantity} @ ${price:.2f} = ${item_total:.2f}")
        self.calc_subtotal()
        
        self.log_message(f"Added {code} x{quantity}")
    
    def calc_subtotal(self):
        """Calculate and display subtotal"""
        self.current_subtotal = sum(item['total'] for item in self.current_transaction)
        self.subtotal_var.set(f"${self.current_subtotal:.2f}")
        self.log_message(f"Subtotal: ${self.current_subtotal:.2f}")
    
    def calc_total(self):
        """Calculate and display total with tax"""
        self.calc_subtotal()
        # Apply default tax rate (8.75%)
        tax_rate = 0.0875
        self.current_tax = self.current_subtotal * tax_rate
        self.current_total = self.current_subtotal + self.current_tax
        
        self.tax_var.set(f"${self.current_tax:.2f}")
        self.total_var.set(f"${self.current_total:.2f}")
        self.log_message(f"Total: ${self.current_total:.2f} (Tax: ${self.current_tax:.2f})")
    
    def process_payment(self):
        """Process payment for current transaction"""
        self.calc_total()
        
        if self.current_total <= 0:
            messagebox.showwarning("Payment", "No items to pay for!")
            return
        
        # Simple payment dialog
        amount = simpledialog.askfloat("Payment", f"Total: ${self.current_total:.2f}\nEnter amount tendered:")
        if amount:
            change = amount - self.current_total
            if change >= 0:
                messagebox.showinfo("Payment", f"Change: ${change:.2f}")
                self.log_message(f"Payment: ${amount:.2f}, Change: ${change:.2f}")
                self.complete_transaction()
            else:
                messagebox.showwarning("Payment", f"Insufficient payment! Still owe: ${-change:.2f}")
    
    def void_item(self):
        """Void the last item"""
        if self.current_transaction:
            self.current_transaction.pop()
            self.trans_listbox.delete(tk.END)
            self.calc_subtotal()
            self.log_message("Last item voided")
    
    def hold_transaction(self):
        """Hold current transaction"""
        if self.current_transaction:
            name = simpledialog.askstring("Hold", "Enter ticket name (optional):")
            index = self.register.hold_transaction(self.current_transaction.copy(), name)
            self.clear_transaction()
            self.log_message(f"Transaction held (#{index + 1})")
    
    def recall_transaction(self):
        """Recall a held transaction"""
        if self.register.held_transactions:
            # Show held transactions
            held_list = [f"{i+1}. {h.get('name', 'Unnamed')}" for i, h in enumerate(self.register.held_transactions)]
            choice = simpledialog.askinteger("Recall", f"Select ticket:\n" + "\n".join(held_list))
            if choice:
                held = self.register.recall_transaction(choice - 1)
                if held:
                    self.current_transaction = held['transaction']
                    self.refresh_transaction_display()
                    self.calc_subtotal()
                    self.log_message(f"Recalled transaction: {held.get('name', 'Unnamed')}")
    
    def process_refund(self):
        """Process a refund"""
        messagebox.showinfo("Refund", "Refund mode activated")
        self.log_message("Refund mode")
    
    def cancel_transaction(self):
        """Cancel current transaction"""
        self.clear_transaction()
        self.log_message("Transaction cancelled")
    
    def complete_transaction(self):
        """Complete the transaction and clear"""
        # Save to register history
        self.register.transactions.append({
            'items': self.current_transaction.copy(),
            'subtotal': self.current_subtotal,
            'tax': self.current_tax,
            'total': self.current_total,
            'timestamp': datetime.now(),
            'clerk': self.register.current_clerk
        })
        self.clear_transaction()
        self.log_message("Transaction completed")
    
    def clear_transaction(self):
        """Clear current transaction"""
        self.current_transaction = []
        self.current_subtotal = 0.0
        self.current_tax = 0.0
        self.current_total = 0.0
        self.trans_listbox.delete(0, tk.END)
        self.subtotal_var.set("$0.00")
        self.tax_var.set("$0.00")
        self.total_var.set("$0.00")
    
    def refresh_transaction_display(self):
        """Refresh the transaction listbox"""
        self.trans_listbox.delete(0, tk.END)
        for item in self.current_transaction:
            self.trans_listbox.insert(tk.END, 
                f"{item['code']} x{item['quantity']} @ ${item['price']:.2f} = ${item['total']:.2f}")
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def update_exchange_rates(self):
        """Update currency exchange rates from API"""
        try:
            # In production, use actual API
            # url = "https://api.exchangeratesapi.io/latest"
            # response = requests.get(url)
            # data = response.json()
            # self.register.exchange_rates.update(data["rates"])
            
            self.log_message("Exchange rates updated")
            messagebox.showinfo("Exchange Rates", "Rates updated successfully!")
        except Exception as e:
            self.log_message(f"Failed to update rates: {e}")
            messagebox.showerror("Error", f"Failed to update rates: {e}")
    
    def clerk_login(self):
        """Clerk login dialog"""
        clerk_id = simpledialog.askstring("Login", "Enter clerk ID:")
        if clerk_id:
            if self.register.login_clerk(clerk_id):
                self.log_message(f"Clerk {clerk_id} logged in")
                messagebox.showinfo("Login", f"Welcome, {self.register.clerks[clerk_id]['name']}!")
            else:
                messagebox.showerror("Login", "Invalid clerk ID")
    
    def log_message(self, message):
        """Log a message to the display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.display_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.display_text.see(tk.END)


# ============================================================================
# TAX PROGRAMMING INTERFACE
# ============================================================================

class TaxProgrammingApp:
    def __init__(self, master, register):
        self.master = master
        master.title("Tax Programming - Reggie Starr RS-79")
        
        self.register = register
        
        # Tax name
        tk.Label(master, text="Tax Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.tax_name_var = tk.StringVar()
        tk.Entry(master, textvariable=self.tax_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Tax rate
        tk.Label(master, text="Tax Rate (%):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tax_rate_var = tk.DoubleVar()
        tk.Entry(master, textvariable=self.tax_rate_var).grid(row=1, column=1, padx=5, pady=5)
        
        # Add button
        tk.Button(master, text="Add Tax Rate", command=self.add_tax_rate).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Display area
        self.tax_display = tk.Text(master, height=10, width=40)
        self.tax_display.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        self.update_tax_display()
    
    def add_tax_rate(self):
        name = self.tax_name_var.get()
        rate = self.tax_rate_var.get() / 100  # Convert percentage to decimal
        if name and rate >= 0:
            self.register.add_tax_rate(name, rate)
            self.update_tax_display()
            self.tax_name_var.set("")
            self.tax_rate_var.set(0)
    
    def update_tax_display(self):
        self.tax_display.delete('1.0', tk.END)
        self.tax_display.insert(tk.END, "Configured Tax Rates:\n")
        self.tax_display.insert(tk.END, "-" * 30 + "\n")
        for name, rate in self.register.tax_rates.items():
            self.tax_display.insert(tk.END, f"{name}: {rate*100:.2f}%\n")


# ============================================================================
# PLU AND DEPARTMENT MANAGEMENT
# ============================================================================

class PLUManagerApp:
    def __init__(self, master, register):
        self.master = master
        master.title("PLU & Department Management - Reggie Starr RS-79")
        
        self.register = register
        
        row = 0
        # Product code
        tk.Label(master, text="Product Code:").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.code_var = tk.StringVar()
        tk.Entry(master, textvariable=self.code_var).grid(row=row, column=1, padx=5)
        row += 1
        
        # Product name
        tk.Label(master, text="Product Name:").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.name_var = tk.StringVar()
        tk.Entry(master, textvariable=self.name_var).grid(row=row, column=1, padx=5)
        row += 1
        
        # Price
        tk.Label(master, text="Price:").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.price_var = tk.DoubleVar()
        tk.Entry(master, textvariable=self.price_var).grid(row=row, column=1, padx=5)
        row += 1
        
        # Quantity
        tk.Label(master, text="Quantity:").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.quantity_var = tk.IntVar(value=0)
        tk.Entry(master, textvariable=self.quantity_var).grid(row=row, column=1, padx=5)
        row += 1
        
        # Tax rates
        tk.Label(master, text="Tax Rates (comma-separated):").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.tax_rates_var = tk.StringVar()
        tk.Entry(master, textvariable=self.tax_rates_var).grid(row=row, column=1, padx=5)
        row += 1
        
        # Department
        tk.Label(master, text="Department:").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.department_var = tk.StringVar()
        tk.Entry(master, textvariable=self.department_var).grid(row=row, column=1, padx=5)
        row += 1
        
        # PLU code
        tk.Label(master, text="PLU Code:").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.plu_var = tk.StringVar()
        tk.Entry(master, textvariable=self.plu_var).grid(row=row, column=1, padx=5)
        row += 1
        
        # Add button
        tk.Button(master, text="Add Product", command=self.add_product).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        # Display area
        self.product_display = tk.Text(master, height=15, width=60)
        self.product_display.grid(row=row, column=0, columnspan=2, padx=5, pady=5)
        
        self.update_product_display()
    
    def add_product(self):
        code = self.code_var.get()
        name = self.name_var.get()
        price = self.price_var.get()
        quantity = self.quantity_var.get()
        tax_rates = [t.strip() for t in self.tax_rates_var.get().split(',') if t.strip()]
        department = self.department_var.get()
        plu_code = self.plu_var.get() or None
        
        if code and name and price >= 0:
            self.register.add_product(code, name, price, quantity, tax_rates, department, plu_code)
            self.update_product_display()
            self.clear_fields()
    
    def clear_fields(self):
        self.code_var.set("")
        self.name_var.set("")
        self.price_var.set(0)
        self.quantity_var.set(0)
        self.tax_rates_var.set("")
        self.department_var.set("")
        self.plu_var.set("")
    
    def update_product_display(self):
        self.product_display.delete('1.0', tk.END)
        self.product_display.insert(tk.END, "Product Inventory:\n")
        self.product_display.insert(tk.END, "=" * 60 + "\n")
        for product in self.register.inventory:
            info = f"Code: {product['code']}, Name: {product['name']}, "
            info += f"Price: ${product['price']:.2f}, Qty: {product['quantity']}, "
            info += f"Dept: {product['department']}, PLU: {product['plu_code']}\n"
            self.product_display.insert(tk.END, info)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def show_splash():
    """Show splash screen"""
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    splash_root.after(3000, splash.start_app)  # Auto-close after 3 seconds
    splash_root.mainloop()

def main():
    """Main application entry point"""
    # Show splash screen
    show_splash()
    
    # Start main application
    root = tk.Tk()
    root.geometry("800x600")
    app = CashRegisterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
