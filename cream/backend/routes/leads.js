const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

// In-memory storage (would be MongoDB in production)
let leads = [];
let leadIdCounter = 1;

/**
 * GET /api/leads
 * Get all leads for the authenticated user
 */
router.get('/', authenticateToken, (req, res) => {
  const userLeads = leads.filter(l => l.userId === req.user.userId);
  res.json({ leads: userLeads });
});

/**
 * GET /api/leads/:id
 * Get a specific lead
 */
router.get('/:id', authenticateToken, (req, res) => {
  const lead = leads.find(l => l.id === parseInt(req.params.id) && l.userId === req.user.userId);
  
  if (!lead) {
    return res.status(404).json({ error: 'Lead not found' });
  }
  
  res.json({ lead });
});

/**
 * POST /api/leads
 * Create a new lead
 */
router.post('/', authenticateToken, (req, res) => {
  const {
    name,
    email,
    phone,
    address,
    city,
    state,
    zip,
    status = 'new',
    source,
    notes,
    propertyType,
    budget,
    timeline
  } = req.body;

  // Validation
  if (!name) {
    return res.status(400).json({ error: 'Name is required' });
  }

  const lead = {
    id: leadIdCounter++,
    userId: req.user.userId,
    name,
    email: email || null,
    phone: phone || null,
    address: address || null,
    city: city || null,
    state: state || null,
    zip: zip || null,
    status, // new, contacted, qualified, proposal, negotiation, closed_won, closed_lost
    source: source || null,
    notes: notes || null,
    propertyType: propertyType || null,
    budget: budget || null,
    timeline: timeline || null,
    score: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  leads.push(lead);

  res.status(201).json({
    message: 'Lead created successfully',
    lead
  });
});

/**
 * PUT /api/leads/:id
 * Update a lead
 */
router.put('/:id', authenticateToken, (req, res) => {
  const leadIndex = leads.findIndex(
    l => l.id === parseInt(req.params.id) && l.userId === req.user.userId
  );

  if (leadIndex === -1) {
    return res.status(404).json({ error: 'Lead not found' });
  }

  const allowedFields = [
    'name', 'email', 'phone', 'address', 'city', 'state', 'zip',
    'status', 'source', 'notes', 'propertyType', 'budget', 'timeline', 'score'
  ];

  // Update only provided fields
  allowedFields.forEach(field => {
    if (req.body[field] !== undefined) {
      leads[leadIndex][field] = req.body[field];
    }
  });

  leads[leadIndex].updatedAt = new Date().toISOString();

  res.json({
    message: 'Lead updated',
    lead: leads[leadIndex]
  });
});

/**
 * DELETE /api/leads/:id
 * Delete a lead
 */
router.delete('/:id', authenticateToken, (req, res) => {
  const leadIndex = leads.findIndex(
    l => l.id === parseInt(req.params.id) && l.userId === req.user.userId
  );

  if (leadIndex === -1) {
    return res.status(404).json({ error: 'Lead not found' });
  }

  const deletedLead = leads.splice(leadIndex, 1);

  res.json({
    message: 'Lead deleted',
    lead: deletedLead[0]
  });
});

/**
 * POST /api/leads/bulk
 * Bulk import leads
 */
router.post('/bulk', authenticateToken, (req, res) => {
  const { leads: newLeads } = req.body;

  if (!Array.isArray(newLeads) || newLeads.length === 0) {
    return res.status(400).json({ error: 'Array of leads required' });
  }

  const createdLeads = [];
  const errors = [];

  newLeads.forEach((leadData, index) => {
    if (!leadData.name) {
      errors.push({ index, error: 'Name is required' });
      return;
    }

    const lead = {
      id: leadIdCounter++,
      userId: req.user.userId,
      name: leadData.name,
      email: leadData.email || null,
      phone: leadData.phone || null,
      address: leadData.address || null,
      city: leadData.city || null,
      state: leadData.state || null,
      zip: leadData.zip || null,
      status: leadData.status || 'new',
      source: leadData.source || null,
      notes: leadData.notes || null,
      propertyType: leadData.propertyType || null,
      budget: leadData.budget || null,
      timeline: leadData.timeline || null,
      score: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    leads.push(lead);
    createdLeads.push(lead);
  });

  res.status(201).json({
    message: `Created ${createdLeads.length} leads`,
    created: createdLeads.length,
    errors: errors.length > 0 ? errors : null
  });
});

/**
 * GET /api/leads/stats/summary
 * Get lead statistics
 */
router.get('/stats/summary', authenticateToken, (req, res) => {
  const userLeads = leads.filter(l => l.userId === req.user.userId);

  const stats = {
    total: userLeads.length,
    byStatus: {},
    avgScore: 0
  };

  userLeads.forEach(lead => {
    stats.byStatus[lead.status] = (stats.byStatus[lead.status] || 0) + 1;
    stats.avgScore += lead.score || 0;
  });

  stats.avgScore = userLeads.length > 0 
    ? Math.round(stats.avgScore / userLeads.length) 
    : 0;

  res.json({ stats });
});

module.exports = router;
