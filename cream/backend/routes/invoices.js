const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

// In-memory storage
let invoices = [];
let invoiceIdCounter = 1;

/**
 * GET /api/invoices
 * Get all invoices
 */
router.get('/', authenticateToken, (req, res) => {
  let userInvoices = invoices.filter(i => i.userId === req.user.userId);
  
  // Filter options
  const { status, client, startDate, endDate } = req.query;
  
  if (status) {
    userInvoices = userInvoices.filter(i => i.status === status);
  }
  if (client) {
    userInvoices = userInvoices.filter(i => 
      i.clientName.toLowerCase().includes(client.toLowerCase())
    );
  }
  if (startDate) {
    userInvoices = userInvoices.filter(i => new Date(i.date) >= new Date(startDate));
  }
  if (endDate) {
    userInvoices = userInvoices.filter(i => new Date(i.date) <= new Date(endDate));
  }
  
  // Sort by date descending
  userInvoices.sort((a, b) => new Date(b.date) - new Date(a.date));
  
  res.json({ invoices: userInvoices });
});

/**
 * GET /api/invoices/:id
 * Get single invoice
 */
router.get('/:id', authenticateToken, (req, res) => {
  const invoice = invoices.find(
    i => i.id === parseInt(req.params.id) && i.userId === req.user.userId
  );
  
  if (!invoice) {
    return res.status(404).json({ error: 'Invoice not found' });
  }
  
  res.json({ invoice });
});

/**
 * POST /api/invoices
 * Create invoice
 */
router.post('/', authenticateToken, (req, res) => {
  const {
    clientName,
    clientEmail,
    clientAddress,
    items = [],
    notes,
    dueDate,
    taxRate = 0
  } = req.body;

  if (!clientName) {
    return res.status(400).json({ error: 'Client name is required' });
  }

  // Calculate totals
  const subtotal = items.reduce((sum, item) => sum + (item.quantity * item.rate), 0);
  const taxAmount = subtotal * (taxRate / 100);
  const total = subtotal + taxAmount;

  const invoice = {
    id: invoiceIdCounter++,
    userId: req.user.userId,
    invoiceNumber: `INV-${String(invoiceIdCounter).padStart(4, '0')}`,
    clientName,
    clientEmail: clientEmail || null,
    clientAddress: clientAddress || null,
    items,
    subtotal,
    taxRate,
    taxAmount,
    total,
    status: 'draft', // draft, sent, paid, overdue, cancelled
    date: new Date().toISOString(),
    dueDate: dueDate || null,
    notes: notes || null,
    paidDate: null,
    paymentMethod: null,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  invoices.push(invoice);

  res.status(201).json({
    message: 'Invoice created',
    invoice
  });
});

/**
 * PUT /api/invoices/:id
 * Update invoice
 */
router.put('/:id', authenticateToken, (req, res) => {
  const index = invoices.findIndex(
    i => i.id === parseInt(req.params.id) && i.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Invoice not found' });
  }

  const allowedFields = [
    'clientName', 'clientEmail', 'clientAddress', 'items',
    'notes', 'dueDate', 'taxRate', 'status'
  ];

  // Update provided fields
  allowedFields.forEach(field => {
    if (req.body[field] !== undefined) {
      invoices[index][field] = req.body[field];
    }
  });

  // Recalculate totals if items changed
  if (req.body.items) {
    const subtotal = req.body.items.reduce((sum, item) => sum + (item.quantity * item.rate), 0);
    const taxRate = invoices[index].taxRate || 0;
    invoices[index].subtotal = subtotal;
    invoices[index].taxAmount = subtotal * (taxRate / 100);
    invoices[index].total = subtotal + invoices[index].taxAmount;
  }

  invoices[index].updatedAt = new Date().toISOString();

  res.json({
    message: 'Invoice updated',
    invoice: invoices[index]
  });
});

/**
 * POST /api/invoices/:id/pay
 * Mark invoice as paid
 */
router.post('/:id/pay', authenticateToken, (req, res) => {
  const { paymentMethod } = req.body;
  
  const index = invoices.findIndex(
    i => i.id === parseInt(req.params.id) && i.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Invoice not found' });
  }

  invoices[index].status = 'paid';
  invoices[index].paidDate = new Date().toISOString();
  invoices[index].paymentMethod = paymentMethod || null;
  invoices[index].updatedAt = new Date().toISOString();

  res.json({
    message: 'Invoice marked as paid',
    invoice: invoices[index]
  });
});

/**
 * DELETE /api/invoices/:id
 * Delete invoice
 */
router.delete('/:id', authenticateToken, (req, res) => {
  const index = invoices.findIndex(
    i => i.id === parseInt(req.params.id) && i.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Invoice not found' });
  }

  const deleted = invoices.splice(index, 1);

  res.json({ message: 'Invoice deleted', invoice: deleted[0] });
});

/**
 * GET /api/invoices/stats/summary
 * Get invoice statistics
 */
router.get('/stats/summary', authenticateToken, (req, res) => {
  const userInvoices = invoices.filter(i => i.userId === req.user.userId);

  const stats = {
    total: userInvoices.length,
    totalRevenue: 0,
    paid: 0,
    pending: 0,
    overdue: 0,
    byMonth: {}
  };

  userInvoices.forEach(inv => {
    stats.totalRevenue += inv.total;
    
    if (inv.status === 'paid') stats.paid++;
    else if (inv.status === 'overdue') stats.overdue++;
    else stats.pending++;

    // By month
    const month = inv.date.substring(0, 7); // YYYY-MM
    if (!stats.byMonth[month]) {
      stats.byMonth[month] = { count: 0, revenue: 0 };
    }
    stats.byMonth[month].count++;
    stats.byMonth[month].revenue += inv.total;
  });

  res.json({ stats });
});

module.exports = router;
