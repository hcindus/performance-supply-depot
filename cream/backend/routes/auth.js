const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// User model (would be MongoDB in production)
const users = [];

// JWT Secret (should be in environment variables)
const JWT_SECRET = process.env.JWT_SECRET || 'cream-secret-key-change-in-production';

/**
 * POST /api/auth/register
 * Register a new user
 */
router.post('/register', async (req, res) => {
  try {
    const { email, password, name, phone, agency } = req.body;

    // Validate required fields
    if (!email || !password || !name) {
      return res.status(400).json({ 
        error: 'Email, password, and name are required' 
      });
    }

    // Check if user already exists
    const existingUser = users.find(u => u.email === email);
    if (existingUser) {
      return res.status(400).json({ 
        error: 'User already exists' 
      });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const user = {
      id: users.length + 1,
      email,
      password: hashedPassword,
      name,
      phone: phone || null,
      agency: agency || null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    users.push(user);

    // Generate token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.status(201).json({
      message: 'User registered successfully',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        phone: user.phone,
        agency: user.agency
      }
    });
  } catch (error) {
    console.error('Register error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

/**
 * POST /api/auth/login
 * Login user
 */
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validate required fields
    if (!email || !password) {
      return res.status(400).json({ 
        error: 'Email and password are required' 
      });
    }

    // Find user
    const user = users.find(u => u.email === email);
    if (!user) {
      return res.status(401).json({ 
        error: 'Invalid credentials' 
      });
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ 
        error: 'Invalid credentials' 
      });
    }

    // Generate token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    res.json({
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        phone: user.phone,
        agency: user.agency
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

/**
 * GET /api/auth/me
 * Get current user (protected)
 */
router.get('/me', authenticateToken, (req, res) => {
  const user = users.find(u => u.id === req.user.userId);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.json({
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      phone: user.phone,
      agency: user.agency,
      createdAt: user.createdAt
    }
  });
});

/**
 * PUT /api/auth/profile
 * Update user profile (protected)
 */
router.put('/profile', authenticateToken, async (req, res) => {
  try {
    const { name, phone, agency } = req.body;
    const userIndex = users.findIndex(u => u.id === req.user.userId);

    if (userIndex === -1) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Update fields
    if (name) users[userIndex].name = name;
    if (phone) users[userIndex].phone = phone;
    if (agency) users[userIndex].agency = agency;
    users[userIndex].updatedAt = new Date().toISOString();

    res.json({
      message: 'Profile updated',
      user: {
        id: users[userIndex].id,
        email: users[userIndex].email,
        name: users[userIndex].name,
        phone: users[userIndex].phone,
        agency: users[userIndex].agency
      }
    });
  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({ error: 'Profile update failed' });
  }
});

/**
 * POST /api/auth/logout
 * Logout user
 */
router.post('/logout', (req, res) => {
  // In a real app, you'd invalidate the token here
  res.json({ message: 'Logged out successfully' });
});

// Middleware to authenticate token
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
}

module.exports = router;
module.exports.authenticateToken = authenticateToken;
