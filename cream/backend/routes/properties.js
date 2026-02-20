const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

// In-memory storage
let properties = [];
let propertyIdCounter = 1;

/**
 * GET /api/properties
 * Get all properties
 */
router.get('/', authenticateToken, (req, res) => {
  let userProperties = properties.filter(p => p.userId === req.user.userId);
  
  // Filters
  const { type, status, minPrice, maxPrice, city, state } = req.query;
  
  if (type) {
    userProperties = userProperties.filter(p => p.type === type);
  }
  if (status) {
    userProperties = userProperties.filter(p => p.status === status);
  }
  if (minPrice) {
    userProperties = userProperties.filter(p => p.price >= parseInt(minPrice));
  }
  if (maxPrice) {
    userProperties = userProperties.filter(p => p.price <= parseInt(maxPrice));
  }
  if (city) {
    userProperties = userProperties.filter(p => 
      p.city.toLowerCase().includes(city.toLowerCase())
    );
  }
  if (state) {
    userProperties = userProperties.filter(p => p.state === state);
  }
  
  res.json({ properties: userProperties });
});

/**
 * GET /api/properties/:id
 * Get single property
 */
router.get('/:id', authenticateToken, (req, res) => {
  const property = properties.find(
    p => p.id === parseInt(req.params.id) && p.userId === req.user.userId
  );
  
  if (!property) {
    return res.status(404).json({ error: 'Property not found' });
  }
  
  res.json({ property });
});

/**
 * POST /api/properties
 * Create property listing
 */
router.post('/', authenticateToken, (req, res) => {
  const {
    address,
    city,
    state,
    zip,
    type, // residential, commercial, land, multi-family
    price,
    bedrooms,
    bathrooms,
    sqft,
    yearBuilt,
    description,
    features = [],
    images = [],
    status = 'active', // active, pending, sold, off-market
    listingDate,
    soldDate,
    mlsNumber,
    coListingAgent
  } = req.body;

  if (!address || !city || !state) {
    return res.status(400).json({ error: 'Address, city, and state are required' });
  }

  const property = {
    id: propertyIdCounter++,
    userId: req.user.userId,
    address,
    city,
    state,
    zip: zip || null,
    type: type || 'residential',
    price: price || null,
    bedrooms: bedrooms || null,
    bathrooms: bathrooms || null,
    sqft: sqft || null,
    yearBuilt: yearBuilt || null,
    description: description || null,
    features,
    images,
    status,
    listingDate: listingDate || new Date().toISOString(),
    soldDate: soldDate || null,
    mlsNumber: mlsNumber || null,
    coListingAgent: coListingAgent || null,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  properties.push(property);

  res.status(201).json({
    message: 'Property created',
    property
  });
});

/**
 * PUT /api/properties/:id
 * Update property
 */
router.put('/:id', authenticateToken, (req, res) => {
  const index = properties.findIndex(
    p => p.id === parseInt(req.params.id) && p.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Property not found' });
  }

  const allowedFields = [
    'address', 'city', 'state', 'zip', 'type', 'price', 'bedrooms',
    'bathrooms', 'sqft', 'yearBuilt', 'description', 'features',
    'images', 'status', 'listingDate', 'soldDate', 'mlsNumber', 'coListingAgent'
  ];

  allowedFields.forEach(field => {
    if (req.body[field] !== undefined) {
      properties[index][field] = req.body[field];
    }
  });

  properties[index].updatedAt = new Date().toISOString();

  res.json({
    message: 'Property updated',
    property: properties[index]
  });
});

/**
 * DELETE /api/properties/:id
 * Delete property
 */
router.delete('/:id', authenticateToken, (req, res) => {
  const index = properties.findIndex(
    p => p.id === parseInt(req.params.id) && p.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Property not found' });
  }

  const deleted = properties.splice(index, 1);

  res.json({ message: 'Property deleted', property: deleted[0] });
});

/**
 * GET /api/properties/stats/summary
 * Get property statistics
 */
router.get('/stats/summary', authenticateToken, (req, res) => {
  const userProperties = properties.filter(p => p.userId === req.user.userId);

  const stats = {
    total: userProperties.length,
    active: 0,
    pending: 0,
    sold: 0,
    offMarket: 0,
    totalValue: 0,
    avgPrice: 0,
    byType: {},
    byCity: {}
  };

  userProperties.forEach(p => {
    stats[p.status === 'active' ? 'active' : 
          p.status === 'pending' ? 'pending' :
          p.status === 'sold' ? 'sold' : 'offMarket']++;
    
    if (p.price) {
      stats.totalValue += p.price;
    }

    // By type
    stats.byType[p.type] = (stats.byType[p.type] || 0) + 1;

    // By city
    stats.byCity[p.city] = (stats.byCity[p.city] || 0) + 1;
  });

  stats.avgPrice = stats.total > 0 
    ? Math.round(stats.totalValue / stats.total) 
    : 0;

  res.json({ stats });
});

module.exports = router;
