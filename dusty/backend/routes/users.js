const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

/**
 * GET /api/users/settings
 */
router.get('/settings', authenticateToken, (req, res) => {
  res.json({
    settings: {
      currency: 'USD',
      theme: 'dark',
      notifications: true,
      networks: ['Ethereum', 'BSC', 'Polygon', 'Arbitrum', 'Optimism', 'Bitgert']
    }
  });
});

/**
 * PUT /api/users/settings
 */
router.put('/settings', authenticateToken, (req, res) => {
  const { currency, theme, notifications, networks } = req.body;
  
  res.json({
    message: 'Settings updated',
    settings: {
      currency: currency || 'USD',
      theme: theme || 'dark',
      notifications: notifications !== undefined ? notifications : true,
      networks: networks || ['Ethereum', 'BSC', 'Polygon', 'Arbitrum', 'Optimism', 'Bitgert']
    }
  });
});

/**
 * GET /api/users/dashboard
 */
router.get('/dashboard', authenticateToken, (req, res) => {
  res.json({
    dashboard: {
      totalValue: '$0.00',
      wallets: 0,
      transactions: 0,
      staking: { total: '$0.00', apy: '0%' },
      recentTransactions: []
    }
  });
});

module.exports = router;
