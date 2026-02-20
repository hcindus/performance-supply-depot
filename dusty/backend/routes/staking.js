const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

// In-memory storage
let stakes = [];
let stakeIdCounter = 1;

/**
 * GET /api/staking/pools
 * Get available staking pools
 */
router.get('/pools', authenticateToken, (req, res) => {
  const { network } = req.query;
  
  // Mock staking pools
  const pools = [
    {
      id: 1,
      name: 'ETH Staking',
      network: 'ethereum',
      token: 'ETH',
      apy: '4.2%',
      minStake: '0.01',
      lockPeriod: 'None',
      rewards: 'ETH'
    },
    {
      id: 2,
      name: 'BSC Validator',
      network: 'bsc',
      token: 'BNB',
      apy: '3.8%',
      minStake: '0.1',
      lockPeriod: '7 days',
      rewards: 'BNB'
    },
    {
      id: 3,
      name: 'Polygon Stake',
      network: 'polygon',
      token: 'MATIC',
      apy: '5.1%',
      minStake: '100',
      lockPeriod: 'None',
      rewards: 'MATIC'
    },
    {
      id: 4,
      name: 'Bitgert Brevis',
      network: 'bitgert',
      token: 'BRISE',
      apy: '12.5%',
      minStake: '1000000',
      lockPeriod: '30 days',
      rewards: 'BRISE + NFT'
    }
  ];
  
  const filtered = network 
    ? pools.filter(p => p.network === network) 
    : pools;
  
  res.json({ pools: filtered });
});

/**
 * GET /api/staking
 * Get user's staking positions
 */
router.get('/', authenticateToken, (req, res) => {
  const userStakes = stakes.filter(s => s.userId === req.user.userId);
  res.json({ stakes: userStakes });
});

/**
 * POST /api/staking
 * Stake tokens
 */
router.post('/', authenticateToken, (req, res) => {
  const { poolId, amount, walletId } = req.body;
  
  if (!poolId || !amount || !walletId) {
    return res.status(400).json({ error: 'poolId, amount, and walletId required' });
  }
  
  const stake = {
    id: stakeIdCounter++,
    userId: req.user.userId,
    poolId: parseInt(poolId),
    walletId,
    amount,
    startDate: new Date().toISOString(),
    rewards: '0',
    nftReward: null,
    status: 'active'
  };
  
  stakes.push(stake);
  
  res.status(201).json({
    message: 'Stake created',
    stake
  });
});

/**
 * POST /api/staking/:id/unstake
 * Unstake tokens
 */
router.post('/:id/unstake', authenticateToken, (req, res) => {
  const stakeIndex = stakes.findIndex(
    s => s.id === parseInt(req.params.id) && s.userId === req.user.userId
  );
  
  if (stakeIndex === -1) {
    return res.status(404).json({ error: 'Stake not found' });
  }
  
  // In production, process unstake
  stakes[stakeIndex].status = 'unstaking';
  stakes[stakeIndex].endDate = new Date().toISOString();
  
  res.json({
    message: 'Unstake initiated',
    stake: stakes[stakeIndex]
  });
});

module.exports = router;
