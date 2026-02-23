// Express Health Middleware
// Add to any Express app

module.exports.healthMiddleware = function(app) {
  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  });
  
  app.get('/health/ready', (req, res) => {
    res.json({ status: 'ready' });
  });
  
  app.get('/health/live', (req, res) => {
    res.json({ status: 'live' });
  });
};

// Export for use
module.exports;
