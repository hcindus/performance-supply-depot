const express = require('express');
const router = express.Router();
const { authenticateToken } = require('./auth');

// In-memory storage
let appointments = [];
let appointmentIdCounter = 1;

/**
 * GET /api/appointments
 * Get all appointments
 */
router.get('/', authenticateToken, (req, res) => {
  const userAppointments = appointments.filter(a => a.userId === req.user.userId);
  
  // Filter by date range if provided
  const { start, end, status } = req.query;
  let filtered = userAppointments;
  
  if (start) {
    filtered = filtered.filter(a => new Date(a.dateTime) >= new Date(start));
  }
  if (end) {
    filtered = filtered.filter(a => new Date(a.dateTime) <= new Date(end));
  }
  if (status) {
    filtered = filtered.filter(a => a.status === status);
  }
  
  // Sort by date
  filtered.sort((a, b) => new Date(a.dateTime) - new Date(b.dateTime));
  
  res.json({ appointments: filtered });
});

/**
 * GET /api/appointments/:id
 * Get single appointment
 */
router.get('/:id', authenticateToken, (req, res) => {
  const appointment = appointments.find(
    a => a.id === parseInt(req.params.id) && a.userId === req.user.userId
  );
  
  if (!appointment) {
    return res.status(404).json({ error: 'Appointment not found' });
  }
  
  res.json({ appointment });
});

/**
 * POST /api/appointments
 * Create appointment
 */
router.post('/', authenticateToken, (req, res) => {
  const {
    title,
    dateTime,
    duration = 60, // minutes
    leadId,
    type = 'showing', // showing, showing, open-house, consultation, closing, other
    location,
    notes,
    reminder = true
  } = req.body;

  if (!title || !dateTime) {
    return res.status(400).json({ error: 'Title and dateTime are required' });
  }

  const appointment = {
    id: appointmentIdCounter++,
    userId: req.user.userId,
    title,
    dateTime,
    duration,
    leadId: leadId || null,
    type,
    location: location || null,
    notes: notes || null,
    status: 'scheduled', // scheduled, completed, cancelled, no_show
    reminder,
    reminderSent: false,
    result: null, // landed, not_landed, pending
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  appointments.push(appointment);

  res.status(201).json({
    message: 'Appointment created',
    appointment
  });
});

/**
 * PUT /api/appointments/:id
 * Update appointment
 */
router.put('/:id', authenticateToken, (req, res) => {
  const index = appointments.findIndex(
    a => a.id === parseInt(req.params.id) && a.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Appointment not found' });
  }

  const allowedFields = [
    'title', 'dateTime', 'duration', 'leadId', 'type',
    'location', 'notes', 'status', 'result'
  ];

  allowedFields.forEach(field => {
    if (req.body[field] !== undefined) {
      appointments[index][field] = req.body[field];
    }
  });

  appointments[index].updatedAt = new Date().toISOString();

  res.json({
    message: 'Appointment updated',
    appointment: appointments[index]
  });
});

/**
 * DELETE /api/appointments/:id
 * Delete appointment
 */
router.delete('/:id', authenticateToken, (req, res) => {
  const index = appointments.findIndex(
    a => a.id === parseInt(req.params.id) && a.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Appointment not found' });
  }

  const deleted = appointments.splice(index, 1);

  res.json({ message: 'Appointment deleted', appointment: deleted[0] });
});

/**
 * GET /api/appointments/upcoming
 * Get upcoming appointments (next 7 days)
 */
router.get('/upcoming', authenticateToken, (req, res) => {
  const now = new Date();
  const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

  const upcoming = appointments
    .filter(a => 
      a.userId === req.user.userId &&
      a.status === 'scheduled' &&
      new Date(a.dateTime) >= now &&
      new Date(a.dateTime) <= nextWeek
    )
    .sort((a, b) => new Date(a.dateTime) - new Date(b.dateTime));

  res.json({ appointments: upcoming });
});

/**
 * POST /api/appointments/:id/result
 * Record appointment result (did they land it?)
 */
router.post('/:id/result', authenticateToken, (req, res) => {
  const { result, notes } = req.body;
  
  const index = appointments.findIndex(
    a => a.id === parseInt(req.params.id) && a.userId === req.user.userId
  );

  if (index === -1) {
    return res.status(404).json({ error: 'Appointment not found' });
  }

  if (!['landed', 'not_landed', 'pending'].includes(result)) {
    return res.status(400).json({ error: 'Result must be: landed, not_landed, or pending' });
  }

  appointments[index].result = result;
  appointments[index].notes = notes || appointments[index].notes;
  appointments[index].status = result === 'pending' ? 'scheduled' : 'completed';
  appointments[index].updatedAt = new Date().toISOString();

  res.json({
    message: 'Result recorded',
    appointment: appointments[index]
  });
});

module.exports = router;
