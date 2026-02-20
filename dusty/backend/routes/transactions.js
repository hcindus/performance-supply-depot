const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

// In-memory storage
let transactions = [];
let txIdCounter = 1;

/**
 * GET /api/transactions
 * Get transaction history
 */
router.get('/', authenticateToken, (req, res) => {
  const { walletId, network, type, limit = 50 } = req.query;
  
  let userTxs = transactions.filter(t => t.userId === req.user.userId);
  
  if (walletId) {
    userTxs = userTxs.filter(t => t.walletId === parseInt(walletId));
  }
  if (network) {
    userTxs = userTxs.filter(t => t.network === network);
  }
  if (type) {
    userTxs = userTxs.filter(t => t.type === type);
  }
  
  // Sort by date descending
  userTxs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  
  // Limit results
  userTxs = userTxs.slice(0, parseInt(limit));
  
  res.json({ transactions: userTxs });
});

/**
 * GET /api/transactions/:id
 * Get specific transaction
 */
router.get('/:id', authenticateToken, (req, res) => {
  const tx = transactions.find(
    t => t.id === parseInt(req.params.id) && t.userId === req.user.userId
  );
  
  if (!tx) {
    return res.status(404).json({ error: 'Transaction not found' });
  }
  
  res.json({ transaction: tx });
});

/**
 * POST /api/transactions
 * Create/send transaction
 */
router.post('/', authenticateToken, (req, res) => {
  const {
    walletId,
    to,
    amount,
    network = 'ethereum',
    token = 'native',
    data
  } = req.body;

  if (!walletId || !to || !amount) {
    return res.status(400).json({ error: 'walletId, to, and amount are required' });
  }

  // In production, sign and broadcast transaction
  const tx = {
    id: txIdCounter++,
    userId: req.user.userId,
    walletId: parseInt(walletId),
    from: '0x...', // Would be wallet address
    to,
    amount,
    network,
    token,
    hash: '0x' + generateRandomHash(),
    status: 'pending', // pending, confirmed, failed
    data: data || null,
    timestamp: new Date().toISOString(),
    confirmedAt: null
  };

  transactions.push(tx);

  res.status(201).json({
    message: 'Transaction created',
    transaction: tx
  });
});

/**
 * GET /api/transactions/pending
 * Get pending transactions
 */
router.get('/pending', authenticateToken, (req, res) => {
  const pending = transactions.filter(
    t => t.userId === req.user.userId && t.status === 'pending'
  );
  
  res.json({ transactions: pending });
});

/**
 * POST /api/transactions/:id/broadcast
 * Broadcast pending transaction
 */
router.post('/:id/broadcast', authenticateToken, (req, res) => {
  const txIndex = transactions.findIndex(
    t => t.id === parseInt(req.params.id) && t.userId === req.user.userId
  );

  if (txIndex === -1) {
    return res.status(404).json({ error: 'Transaction not found' });
  }

  // In production, broadcast to network
  transactions[txIndex].status = 'confirmed';
  transactions[txIndex].confirmedAt = new Date().toISOString();

  res.json({
    message: 'Transaction confirmed',
    transaction: transactions[txIndex]
  });
});

// Helper: Generate random hash
function generateRandomHash() {
  const chars = '0123456789abcdef';
  let hash = '';
  for (let i = 0; i < 64; i++) {
    hash += chars[Math.floor(Math.random() * 16)];
  }
  return hash;
}

module.exports = router;
