// TEC MA-79 Digital Cash Register
// Complete implementation based on Owner's Manual pages 26-35

// ==================== CONFIGURATION ====================

var CONFIG = {
    currency: "USD", // USD, EUR, GBP, BTC, etc.
    language: "English", // English, Spanish, French, German, Arabic, Chinese, Korean, Japanese
    taxRates: [
        { name: "Standard", rate: 0.08 },
        { name: "Reduced", rate: 0.05 },
        { name: "Exempt", rate: 0.00 }
    ],
    paymentMethods: ["Cash", "BTC", "MC/Visa", "AMEX", "EBT", "WIC", "Debit", "Check"],
    storeName: "Performance Supply Depot",
    storeAddress: "",
    receiptFooter: "Thank you for your business!"
};

// ==================== DATA STRUCTURES ====================

var PLU_DATABASE = {}; // Price Look-Up database
var DEPARTMENTS = {};
var CLERKS = {};
var TRANSACTION_LOG = [];
var INVENTORY = {};
var CURRENT_TRANSACTION = null;
var CURRENT_MODE = "REGISTER"; // REGISTER, VOID, X, Z, PROGRAM, SERVICE, NEGATIVE
var CURRENT_CLERK = null;

// ==================== MODES ====================

const MODES = {
    REGISTER: {
        name: "Register Mode",
        description: "Normal sales transactions",
        allowed: ["sale", "refund", "discount", "payment"]
    },
    VOID: {
        name: "Void Mode",
        description: "Cancel previous transactions",
        allowed: ["void", "cancel"]
    },
    X: {
        name: "X Mode (Read)",
        description: "Read reports without resetting",
        allowed: ["report", "inquiry"]
    },
    Z: {
        name: "Z Mode (Reset)",
        description: "Read and reset reports",
        allowed: ["report", "reset"]
    },
    PROGRAM: {
        name: "Program Mode",
        description: "Configure settings, PLUs, taxes",
        allowed: ["program"]
    },
    SERVICE: {
        name: "Service Mode",
        description: "Maintenance and diagnostics",
        allowed: ["service"]
    },
    NEGATIVE: {
        name: "Negative Mode",
        description: "Returns and negative entries",
        allowed: ["return", "negative"]
    }
};

// ==================== PLU MANAGEMENT ====================

function createPLU(code, name, price, department, taxRate, openPrice) {
    PLU_DATABASE[code] = {
        code: code,
        name: name,
        price: price,
        department: department,
        taxRate: taxRate || 0,
        openPrice: openPrice || false, // Allow price override
        stock: 0,
        trackInventory: false
    };
    return PLU_DATABASE[code];
}

function updatePLU(code, updates) {
    if (PLU_DATABASE[code]) {
        Object.assign(PLU_DATABASE[code], updates);
        return true;
    }
    return false;
}

function deletePLU(code) {
    delete PLU_DATABASE[code];
}

// ==================== DEPARTMENT MANAGEMENT ====================

function createDepartment(code, name, taxRate, group) {
    DEPARTMENTS[code] = {
        code: code,
        name: name,
        taxRate: taxRate || 0,
        group: group || "General",
        sales: 0,
        count: 0
    };
    return DEPARTMENTS[code];
}

// ==================== CLERK MANAGEMENT ====================

function createClerk(id, name, pin, permissions) {
    CLERKS[id] = {
        id: id,
        name: name,
        pin: pin,
        permissions: permissions || ["sale", "refund", "void"],
        sales: 0,
        transactions: 0,
        loginTime: null,
        active: false
    };
    return CLERKS[id];
}

function loginClerk(id, pin) {
    var clerk = CLERKS[id];
    if (clerk && clerk.pin === pin) {
        clerk.active = true;
        clerk.loginTime = new Date();
        CURRENT_CLERK = clerk;
        return true;
    }
    return false;
}

function logoutClerk() {
    if (CURRENT_CLERK) {
        CURRENT_CLERK.active = false;
        CURRENT_CLERK.loginTime = null;
        CURRENT_CLERK = null;
    }
}

// ==================== TRANSACTION ====================

function startTransaction() {
    if (!CURRENT_CLERK) {
        app.ShowPopup("Error: No clerk logged in");
        return null;
    }
    
    CURRENT_TRANSACTION = {
        id: generateTransactionId(),
        clerk: CURRENT_CLERK.id,
        clerkName: CURRENT_CLERK.name,
        startTime: new Date(),
        items: [],
        subtotal: 0,
        tax: 0,
        discounts: 0,
        surcharges: 0,
        total: 0,
        payments: [],
        status: "open", // open, suspended, completed, voided
        mode: CURRENT_MODE
    };
    return CURRENT_TRANSACTION;
}

function generateTransactionId() {
    return "TXN-" + Date.now() + "-" + Math.floor(Math.random() * 1000);
}

function addItem(pluCode, quantity, overridePrice) {
    if (!CURRENT_TRANSACTION || CURRENT_TRANSACTION.status !== "open") {
        app.ShowPopup("Error: No active transaction");
        return false;
    }
    
    var plu = PLU_DATABASE[pluCode];
    if (!plu) {
        app.ShowPopup("Error: PLU not found: " + pluCode);
        return false;
    }
    
    var price = overridePrice || plu.price;
    if (!plu.openPrice && overridePrice) {
        app.ShowPopup("Error: Price override not allowed for this item");
        return false;
    }
    
    var itemTotal = price * quantity;
    var tax = itemTotal * plu.taxRate;
    
    var item = {
        plu: pluCode,
        name: plu.name,
        quantity: quantity,
        price: price,
        taxRate: plu.taxRate,
        tax: tax,
        total: itemTotal + tax,
        department: plu.department,
        voided: false
    };
    
    CURRENT_TRANSACTION.items.push(item);
    recalculateTransaction();
    
    // Update inventory if tracked
    if (plu.trackInventory) {
        plu.stock -= quantity;
    }
    
    return true;
}

function applyDiscount(type, value, target) {
    if (!CURRENT_TRANSACTION) return false;
    
    var discount = {
        type: type, // "percentage" or "flat"
        value: value,
        target: target || "subtotal", // "subtotal", "item", "department"
        applied: false
    };
    
    if (type === "percentage") {
        discount.amount = CURRENT_TRANSACTION.subtotal * (value / 100);
    } else {
        discount.amount = value;
    }
    
    CURRENT_TRANSACTION.discounts += discount.amount;
    discount.applied = true;
    recalculateTransaction();
    return true;
}

function applySurcharge(type, value, description) {
    if (!CURRENT_TRANSACTION) return false;
    
    var surcharge = {
        type: type,
        value: value,
        description: description,
        amount: type === "percentage" ? CURRENT_TRANSACTION.subtotal * (value / 100) : value
    };
    
    CURRENT_TRANSACTION.surcharges += surcharge.amount;
    recalculateTransaction();
    return true;
}

function recalculateTransaction() {
    if (!CURRENT_TRANSACTION) return;
    
    var subtotal = 0;
    var tax = 0;
    
    CURRENT_TRANSACTION.items.forEach(item => {
        if (!item.voided) {
            subtotal += item.price * item.quantity;
            tax += item.tax;
        }
    });
    
    CURRENT_TRANSACTION.subtotal = subtotal;
    CURRENT_TRANSACTION.tax = tax;
    CURRENT_TRANSACTION.total = subtotal + tax - CURRENT_TRANSACTION.discounts + CURRENT_TRANSACTION.surcharges;
}

function voidItem(index) {
    if (!CURRENT_TRANSACTION || !CURRENT_TRANSACTION.items[index]) return false;
    
    CURRENT_TRANSACTION.items[index].voided = true;
    recalculateTransaction();
    return true;
}

function voidTransaction() {
    if (!CURRENT_TRANSACTION) return false;
    
    CURRENT_TRANSACTION.status = "voided";
    logTransaction(CURRENT_TRANSACTION);
    CURRENT_TRANSACTION = null;
    return true;
}

function addPayment(method, amount) {
    if (!CURRENT_TRANSACTION) return false;
    
    var payment = {
        method: method,
        amount: amount,
        time: new Date()
    };
    
    CURRENT_TRANSACTION.payments.push(payment);
    
    var totalPaid = CURRENT_TRANSACTION.payments.reduce((sum, p) => sum + p.amount, 0);
    
    if (totalPaid >= CURRENT_TRANSACTION.total) {
        CURRENT_TRANSACTION.status = "completed";
        CURRENT_TRANSACTION.change = totalPaid - CURRENT_TRANSACTION.total;
        completeTransaction();
    }
    
    return true;
}

function completeTransaction() {
    if (!CURRENT_TRANSACTION) return;
    
    CURRENT_TRANSACTION.endTime = new Date();
    
    // Update clerk stats
    if (CURRENT_CLERK) {
        CURRENT_CLERK.sales += CURRENT_TRANSACTION.total;
        CURRENT_CLERK.transactions++;
    }
    
    // Update department stats
    CURRENT_TRANSACTION.items.forEach(item => {
        if (!item.voided && DEPARTMENTS[item.department]) {
            DEPARTMENTS[item.department].sales += item.total;
            DEPARTMENTS[item.department].count += item.quantity;
        }
    });
    
    logTransaction(CURRENT_TRANSACTION);
    printReceipt(CURRENT_TRANSACTION);
    CURRENT_TRANSACTION = null;
}

function suspendTransaction() {
    if (!CURRENT_TRANSACTION) return null;
    
    CURRENT_TRANSACTION.status = "suspended";
    var recallId = CURRENT_TRANSACTION.id;
    logTransaction(CURRENT_TRANSACTION);
    CURRENT_TRANSACTION = null;
    return recallId;
}

function recallTransaction(transactionId) {
    // In real implementation, retrieve from log
    app.ShowPopup("Recalling transaction: " + transactionId);
}

// ==================== SPECIAL FUNCTIONS ====================

function paidOut(amount, description) {
    // Record money removed from drawer
    var po = {
        type: "PAID_OUT",
        amount: amount,
        description: description,
        clerk: CURRENT_CLERK ? CURRENT_CLERK.id : "unknown",
        time: new Date()
    };
    TRANSACTION_LOG.push(po);
    return true;
}

function paidIn(amount, description) {
    // Record money added to drawer
    var pi = {
        type: "PAID_IN",
        amount: amount,
        description: description,
        clerk: CURRENT_CLERK ? CURRENT_CLERK.id : "unknown",
        time: new Date()
    };
    TRANSACTION_LOG.push(pi);
    return true;
}

function noSale() {
    // Open drawer without transaction
    if (!CURRENT_CLERK) {
        app.ShowPopup("Error: No clerk logged in");
        return false;
    }
    
    var ns = {
        type: "NO_SALE",
        clerk: CURRENT_CLERK.id,
        time: new Date()
    };
    TRANSACTION_LOG.push(ns);
    app.ShowPopup("Drawer opened");
    return true;
}

function priceInquiry(pluCode) {
    var plu = PLU_DATABASE[pluCode];
    if (plu) {
        app.ShowPopup(plu.name + ": " + formatCurrency(plu.price));
        return plu.price;
    }
    app.ShowPopup("PLU not found");
    return null;
}

// ==================== REPORTING ====================

function generateReport(type, period) {
    var report = {
        type: type,
        period: period,
        generated: new Date(),
        data: {}
    };
    
    switch(type) {
        case "FINANCIAL":
            report.data = generateFinancialReport(period);
            break;
        case "DEPARTMENT":
            report.data = generateDepartmentReport(period);
            break;
        case "PLU":
            report.data = generatePLUReport(period);
            break;
        case "CLERK":
            report.data = generateClerkReport(period);
            break;
        case "TAX":
            report.data = generateTaxReport(period);
            break;
        case "INVENTORY":
            report.data = generateInventoryReport();
            break;
    }
    
    return report;
}

function generateFinancialReport(period) {
    var transactions = getTransactionsForPeriod(period);
    var sales = 0;
    var refunds = 0;
    var discounts = 0;
    var tax = 0;
    var paymentTotals = {};
    
    transactions.forEach(txn => {
        if (txn.status === "completed") {
            sales += txn.subtotal;
            tax += txn.tax;
            discounts += txn.discounts;
            
            txn.payments.forEach(p => {
                paymentTotals[p.method] = (paymentTotals[p.method] || 0) + p.amount;
            });
        } else if (txn.status === "voided") {
            refunds += txn.total;
        }
    });
    
    return {
        grossSales: sales,
        netSales: sales - discounts,
        tax: tax,
        discounts: discounts,
        refunds: refunds,
        total: sales + tax - discounts - refunds,
        payments: paymentTotals,
        transactionCount: transactions.filter(t => t.status === "completed").length
    };
}

function generateDepartmentReport(period) {
    var report = {};
    Object.keys(DEPARTMENTS).forEach(code => {
        var dept = DEPARTMENTS[code];
        report[code] = {
            name: dept.name,
            sales: dept.sales,
            count: dept.count
        };
    });
    return report;
}

function generateClerkReport(period) {
    var report = {};
    Object.keys(CLERKS).forEach(id => {
        var clerk = CLERKS[id];
        report[id] = {
            name: clerk.name,
            sales: clerk.sales,
            transactions: clerk.transactions
        };
    });
    return report;
}

function getTransactionsForPeriod(period) {
    var now = new Date();
    var start;
    
    switch(period) {
        case "DAILY":
            start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            break;
        case "WEEKLY":
            start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case "MONTHLY":
            start = new Date(now.getFullYear(), now.getMonth(), 1);
            break;
        case "YEARLY":
            start = new Date(now.getFullYear(), 0, 1);
            break;
        default:
            start = new Date(0);
    }
    
    return TRANSACTION_LOG.filter(txn => txn.startTime && txn.startTime >= start);
}

// ==================== INVENTORY ====================

function updateStock(pluCode, quantity, reason) {
    var plu = PLU_DATABASE[pluCode];
    if (!plu) return false;
    
    plu.stock += quantity;
    
    INVENTORY[pluCode] = INVENTORY[pluCode] || [];
    INVENTORY[pluCode].push({
        date: new Date(),
        adjustment: quantity,
        reason: reason,
        newStock: plu.stock
    });
    
    return true;
}

function generateInventoryReport() {
    var report = {};
    Object.keys(PLU_DATABASE).forEach(code => {
        var plu = PLU_DATABASE[code];
        if (plu.trackInventory) {
            report[code] = {
                name: plu.name,
                stock: plu.stock,
                status: plu.stock < 10 ? "LOW" : plu.stock === 0 ? "OUT" : "OK"
            };
        }
    });
    return report;
}

// ==================== RECEIPT ====================

function printReceipt(transaction) {
    var receipt = [];
    
    receipt.push("=".repeat(40));
    receipt.push("  " + CONFIG.storeName);
    receipt.push("  " + CONFIG.storeAddress);
    receipt.push("=".repeat(40));
    receipt.push("TRANSACTION: " + transaction.id);
    receipt.push("CLERK: " + transaction.clerkName);
    receipt.push("DATE: " + transaction.startTime.toLocaleString());
    receipt.push("-".repeat(40));
    
    transaction.items.forEach(item => {
        if (!item.voided) {
            var line = item.name.substring(0, 20).padEnd(20);
            line += ("x" + item.quantity).padStart(4);
            line += formatCurrency(item.price).padStart(8);
            line += formatCurrency(item.total).padStart(8);
            receipt.push(line);
        }
    });
    
    receipt.push("-".repeat(40));
    receipt.push("SUBTOTAL: " + formatCurrency(transaction.subtotal).padStart(30));
    receipt.push("TAX: " + formatCurrency(transaction.tax).padStart(37));
    if (transaction.discounts > 0) {
        receipt.push("DISCOUNTS: " + formatCurrency(-transaction.discounts).padStart(28));
    }
    receipt.push("TOTAL: " + formatCurrency(transaction.total).padStart(33));
    receipt.push("-".repeat(40));
    
    transaction.payments.forEach(p => {
        receipt.push(p.method + ": " + formatCurrency(p.amount).padStart(33 - p.method.length));
    });
    
    if (transaction.change > 0) {
        receipt.push("CHANGE: " + formatCurrency(transaction.change).padStart(32));
    }
    
    receipt.push("=".repeat(40));
    receipt.push(CONFIG.receiptFooter);
    receipt.push("=".repeat(40));
    
    return receipt.join("\n");
}

// ==================== UTILITIES ====================

function formatCurrency(amount) {
    var symbol = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "BTC": "₿"
    }[CONFIG.currency] || "$";
    
    return symbol + amount.toFixed(2);
}

function logTransaction(transaction) {
    TRANSACTION_LOG.push(transaction);
    // In real implementation, persist to storage
}

function setMode(mode) {
    if (MODES[mode]) {
        CURRENT_MODE = mode;
        app.ShowPopup("Mode: " + MODES[mode].name);
        return true;
    }
    return false;
}

// ==================== DROIDSCRIPT UI ====================

var layMain, layDisplay, layKeys;
var txtDisplay, txtStatus;

function OnStart() {
    app.SetOrientation("Portrait");
    
    // Initialize sample data
    initializeSampleData();
    
    // Create main layout
    layMain = app.CreateLayout("Linear", "Vertical,FillXY");
    layMain.SetBackColor("#1a1a2e");
    
    // Status bar
    var layStatus = app.CreateLayout("Linear", "Horizontal");
    layStatus.SetSize(1, 0.05);
    
    txtStatus = app.CreateText("REGISTER MODE | " + CONFIG.currency, 0.7, -1);
    txtStatus.SetTextColor("#00FF00");
    layStatus.AddChild(txtStatus);
    
    var btnMode = app.CreateButton("MODE", 0.15, 0.05);
    btnMode.SetOnTouch(showModeMenu);
    layStatus.AddChild(btnMode);
    
    var btnClerk = app.CreateButton("CLERK", 0.15, 0.05);
    btnClerk.SetOnTouch(showClerkMenu);
    layStatus.AddChild(btnClerk);
    
    layMain.AddChild(layStatus);
    
    // Display area
    layDisplay = app.CreateLayout("Linear", "Vertical");
    layDisplay.SetSize(1, 0.35);
    layDisplay.SetBackColor("#000000");
    layDisplay.SetPadding(0.02, 0.02, 0.02, 0.02);
    
    txtDisplay = app.CreateText("TEC MA-79\nReady", 1, -1, "Multiline,Left");
    txtDisplay.SetTextColor("#00FF00");
    txtDisplay.SetTextSize(14);
    txtDisplay.SetFont("Monospace");
    layDisplay.AddChild(txtDisplay);
    
    layMain.AddChild(layDisplay);
    
    // Keypad
    createKeypad();
    
    app.AddLayout(layMain);
    
    // Auto-login demo clerk
    createClerk("001", "Demo Clerk", "1234", ["sale", "refund", "void", "discount"]);
    loginClerk("001", "1234");
}

function initializeSampleData() {
    // Create departments
    createDepartment("01", "Groceries", 0.08);
    createDepartment("02", "Beverages", 0.08);
    createDepartment("03", "Electronics", 0.08);
    createDepartment("04", "Services", 0.00);
    
    // Create sample PLUs
    createPLU("1001", "Apple", 0.50, "01", 0.08);
    createPLU("1002", "Bread", 2.99, "01", 0.08);
    createPLU("1003", "Soda", 1.50, "02", 0.08);
    createPLU("1004", "Repair", 25.00, "04", 0.00, true); // Open price
}

function createKeypad() {
    layKeys = app.CreateLayout("Linear", "Vertical");
    layKeys.SetSize(1, 0.6);
    
    var keys = [
        ["PLU", "1", "2", "3", "QTY"],
        ["DEPT", "4", "5", "6", "DISC"],
        ["CLERK", "7", "8", "9", "PAY"],
        ["MODE", "0", "00", ".", "ENTER"]
    ];
    
    keys.forEach(row => {
        var layRow = app.CreateLayout("Linear", "Horizontal");
        layRow.SetSize(1, 0.15);
        
        row.forEach(key => {
            var btn = app.CreateButton(key, 0.2, 0.14);
            btn.SetOnTouch(function() { handleKey(key); });
            
            if (["PLU", "DEPT", "CLERK", "MODE"].includes(key)) {
                btn.SetBackColor("#333333");
                btn.SetTextColor("#FFFFFF");
            } else if (["QTY", "DISC", "PAY", "ENTER"].includes(key)) {
                btn.SetBackColor("#0066CC");
                btn.SetTextColor("#FFFFFF");
            } else {
                btn.SetBackColor("#666666");
                btn.SetTextColor("#FFFFFF");
            }
            
            layRow.AddChild(btn);
        });
        
        layKeys.AddChild(layRow);
    });
    
    layMain.AddChild(layKeys);
}

var inputBuffer = "";
var lastFunction = null;

function handleKey(key) {
    switch(key) {
        case "0": case "1": case "2": case "3":
        case "4": case "5": case "6": case "7":
        case "8": case "9": case "00": case ".":
            inputBuffer += key;
            updateDisplay();
            break;
            
        case "PLU":
            if (inputBuffer) {
                addItem(inputBuffer, 1);
                inputBuffer = "";
                updateDisplay();
            }
            lastFunction = "PLU";
            break;
            
        case "QTY":
            if (inputBuffer && lastFunction === "PLU") {
                // Apply quantity to last item
                inputBuffer = "";
            }
            lastFunction = "QTY";
            break;
            
        case "PAY":
            showPaymentMenu();
            break;
            
        case "DISC":
            if (inputBuffer) {
                applyDiscount("percentage", parseFloat(inputBuffer));
                inputBuffer = "";
                updateDisplay();
            }
            break;
            
        case "ENTER":
            if (CURRENT_TRANSACTION) {
                completeTransaction();
                updateDisplay();
            }
            break;
    }
}

function updateDisplay() {
    var text = "TEC MA-79 Digital Register\n";
    text += "Mode: " + CURRENT_MODE + "\n";
    
    if (CURRENT_CLERK) {
        text += "Clerk: " + CURRENT_CLERK.name + "\n";
    } else {
        text += "Clerk: NOT LOGGED IN\n";
    }
    
    text += "-".repeat(30) + "\n";
    
    if (CURRENT_TRANSACTION) {
        CURRENT_TRANSACTION.items.forEach((item, i) => {
            text += (i + 1) + ". " + item.name.substring(0, 15);
            text += " x" + item.quantity;
            text += " " + formatCurrency(item.total) + "\n";
        });
        text += "-".repeat(30) + "\n";
        text += "TOTAL: " + formatCurrency(CURRENT_TRANSACTION.total) + "\n";
    } else {
        text += "No active transaction\n";
    }
    
    if (inputBuffer) {
        text += "\nInput: " + inputBuffer;
    }
    
    txtDisplay.SetText(text);
}

function showModeMenu() {
    var layDlg = app.CreateLayout("Linear", "Vertical");
    
    Object.keys(MODES).forEach(mode => {
        var btn = app.CreateButton(MODES[mode].name, 0.8, 0.1);
        btn.SetOnTouch(function() {
            setMode(mode);
            dlg.Dismiss();
        });
        layDlg.AddChild(btn);
    });
    
    var dlg = app.CreateDialog("Select Mode");
    dlg.AddLayout(layDlg);
    dlg.Show();
}

function showClerkMenu() {
    if (CURRENT_CLERK) {
        logoutClerk();
        app.ShowPopup("Logged out");
    } else {
        // Simple login dialog
        var layDlg = app.CreateLayout("Linear", "Vertical");
        
        var txtId = app.CreateTextEdit("001", 0.8, 0.1);
        layDlg.AddChild(txtId);
        
        var txtPin = app.CreateTextEdit("1234", 0.8, 0.1);
        txtPin.SetInputType("password");
        layDlg.AddChild(txtPin);
        
        var btnLogin = app.CreateButton("LOGIN", 0.8, 0.1);
        btnLogin.SetOnTouch(function() {
            if (loginClerk(txtId.GetText(), txtPin.GetText())) {
                app.ShowPopup("Welcome, " + CURRENT_CLERK.name);
                dlg.Dismiss();
                updateDisplay();
            } else {
                app.ShowPopup("Invalid credentials");
            }
        });
        layDlg.AddChild(btnLogin);
        
        var dlg = app.CreateDialog("Clerk Login");
        dlg.AddLayout(layDlg);
        dlg.Show();
    }
}

function showPaymentMenu() {
    if (!CURRENT_TRANSACTION || CURRENT_TRANSACTION.total <= 0) {
        app.ShowPopup("No transaction to pay");
        return;
    }
    
    var layDlg = app.CreateLayout("Linear", "Vertical");
    
    CONFIG.paymentMethods.forEach(method => {
        var btn = app.CreateButton(method + " - " + formatCurrency(CURRENT_TRANSACTION.total), 0.8, 0.1);
        btn.SetOnTouch(function() {
            addPayment(method, CURRENT_TRANSACTION.total);
            dlg.Dismiss();
            updateDisplay();
            app.ShowPopup("Payment accepted");
        });
        layDlg.AddChild(btn);
    });
    
    var dlg = app.CreateDialog("Payment Method");
    dlg.AddLayout(layDlg);
    dlg.Show();
}

// Start the application
OnStart();
