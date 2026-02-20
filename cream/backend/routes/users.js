const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

/**
 * GET /api/users/profile
 * Get user profile (same as /auth/me but more detailed)
 */
router.get('/profile', authenticateToken, (req, res) => {
  // In production, fetch from database with more details
  res.json({
    profile: {
      userId: req.user.userId,
      email: req.user.email,
      // Add more fields as needed
      settings: {
        notifications: true,
        timezone: 'America/Los_Angeles'
      }
    }
  });
});

/**
 * PUT /api/users/settings
 * Update user settings
 */
router.put('/settings', authenticateToken, (req, res) => {
  const { notifications, timezone, theme } = req.body;
  
  // In production, save to database
  res.json({
    message: 'Settings updated',
    settings: {
      notifications: notifications !== undefined ? notifications : true,
      timezone: timezone || 'America/Los_Angeles',
      theme: theme || 'light'
    }
  });
});

/**
 * GET /api/users/dashboard
 * Get dashboard data
 */
router.get('/dashboard', authenticateToken, (req, res) => {
  // In production, aggregate from various endpoints
  res.json({
    dashboard: {
      leads: { total: 0, newThisMonth: 0 },
      appointments: { upcoming: 0, completedThisMonth: 0 },
      revenue: { month: 0, year: 0 },
      properties: { active: 0, soldThisMonth: 0 }
    }
  });
});

module.exports = router;
