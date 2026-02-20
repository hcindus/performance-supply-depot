const express = require("express");
const { router: tasksRouter } = require("./routes/tasks");

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// GET /status - Server status endpoint
app.get("/status", (req, res) => {
  res.json({
    ok: true,
    status: "idle",
    timestamp: new Date().toISOString()
  });
});

// GET /health - Health check endpoint (standard format)
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    service: "dusty-core-agent",
    port: PORT,
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// Mount task routes
app.use("/tasks", tasksRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ ok: false, error: "Not found" });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(`[${new Date().toISOString()}] Error:`, err.message);
  res.status(500).json({ ok: false, error: "Internal server error" });
});

// Start server
app.listen(PORT, () => {
  console.log(`[${new Date().toISOString()}] Dusty core-agent server running on port ${PORT}`);
});

module.exports = app;
