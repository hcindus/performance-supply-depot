const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

// In-memory storage
let wallets = [];
let walletIdCounter = 1;

/**
 * GET /api/wallet
 * Get all wallets for user
 */
router.get('/', authenticateToken, (req, res) => {
  const userWallets = wallets.filter(w => w.userId === req.user.userId);
  res.json({ wallets: userWallets });
});

/**
 * GET /api/wallet/:id
 * Get specific wallet
 */
router.get('/:id', authenticateToken, (req, res) => {
  const wallet = wallets.find(
    w => w.id === parseInt(req.params.id) && w.userId === req.user.userId
  );
  
  if (!wallet) {
    return res.status(404).json({ error: 'Wallet not found' });
  }
  
  res.json({ wallet });
});

/**
 * POST /api/wallet
 * Create new wallet
 */
router.post('/', authenticateToken, (req, res) => {
  const { name, network = 'ethereum' } = req.body;

  if (!name) {
    return res.status(400).json({ error: 'Wallet name is required' });
  }

  const wallet = {
    id: walletIdCounter++,
    userId: req.user.userId,
    name,
    address: generateRandomAddress(),
    network,
    balance: {},
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  wallets.push(wallet);

  res.status(201).json({
    message: 'Wallet created',
    wallet
  });
});

/**
 * POST /api/wallet/:id/import
 * Import existing wallet
 */
router.post('/:id/import', authenticateToken, (req, res) => {
  const { privateKey } = req.body;
  
  const walletIndex = wallets.findIndex(
    w => w.id === parseInt(req.params.id) && w.userId === req.user.userId
  );

  if (walletIndex === -1) {
    return res.status(404).json({ error: 'Wallet not found' });
  }

  if (!privateKey) {
    return res.status(400).json({ error: 'Private key is required' });
  }

  // In production, derive address from private key
  wallets[walletIndex].imported = true;
  wallets[walletIndex].updatedAt = new Date().toISOString();

  res.json({
    message: 'Wallet imported',
    wallet: wallets[walletIndex]
  });
});

/**
 * GET /api/wallet/:id/balance
 * Get wallet balance
 */
router.get('/:id/balance', authenticateToken, async (req, res) => {
  const wallet = wallets.find(
    w => w.id === parseInt(req.params.id) && w.userId === req.user.userId
  );
  
  if (!wallet) {
    return res.status(404).json({ error: 'Wallet not found' });
  }

  // In production, query blockchain RPC
  // For now, return mock balances
  const balances = {
    [wallet.network || 'ethereum']: {
      native: '0.0',
      tokens: []
    }
  };

  res.json({
    walletId: wallet.id,
    balances
  });
});

/**
 * GET /api/wallet/:id/dust
 * Scan for dust tokens
 */
router.get('/:id/dust', authenticateToken, async (req, res) => {
  const wallet = wallets.find(
    w => w.id === parseInt(req.params.id) && w.userId === req.user.userId
  );
  
  if (!wallet) {
    return res.status(404).json({ error: 'Wallet not found' });
  }

  // In production, scan token balances
  // Return mock dust data
  const dust = {
    totalValue: '$0.00',
    tokens: [],
    recommendation: 'No dust found'
  };

  res.json({
    walletId: wallet.id,
    dust
  });
});

/**
 * DELETE /api/wallet/:id
 * Delete wallet
 */
router.delete('/:id', authenticateToken, (req, res) => {
  const index = wallets.findIndex(
    w => w.id === parseInt(req.params.id) && w.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Wallet not found' });
  }

  const deleted = wallets.splice(index, 1);

  res.json({ message: 'Wallet deleted', wallet: deleted[0] });
});

// Helper: Generate random address
function generateRandomAddress() {
  const chars = '0123456789abcdef';
  let address = '0x';
  for (let i = 0; i < 40; i++) {
    address += chars[Math.floor(Math.random() * 16)];
  }
  return address;
}

module.exports = router;
