const express = require("express");
const { v4: uuidv4 } = require("uuid");
const axios = require("axios");

const router = express.Router();
const OPENCLAW_URL = process.env.OPENCLAW_URL || "http://localhost:4000/receive_message";

// In-memory task store
const tasks = new Map();

// GET /tasks/:id - Get task status
router.get("/:id", (req, res) => {
  const task = tasks.get(req.params.id);
  if (!task) {
    return res.status(404).json({ ok: false, error: "Task not found" });
  }
  res.json({ ok: true, task });
});

// POST /tasks/:id/complete - Mark task complete
router.post("/:id/complete", (req, res) => {
  const task = tasks.get(req.params.id);
  if (!task) {
    return res.status(404).json({ ok: false, error: "Task not found" });
  }
  task.status = "completed";
  task.completedAt = new Date().toISOString();
  tasks.set(req.params.id, task);
  res.json({ ok: true, task });
});

// POST /tasks - Create new task
router.post("/", async (req, res) => {
  const { type, payload } = req.body;
  
  if (!type) {
    return res.status(400).json({ ok: false, error: "Missing required field: type" });
  }

  const id = uuidv4();
  const task = {
    id,
    type,
    payload: payload || {},
    status: "pending",
    createdAt: new Date().toISOString(),
    completedAt: null
  };

  tasks.set(id, task);
  console.log(`[${new Date().toISOString()}] Task created: ${id} (${type})`);

  // Forward telegram messages to OpenClaw mock
  let openclawResponse = null;
  if (type === 'telegram_message' && payload.text) {
    try {
      console.log(`[${new Date().toISOString()}] Forwarding to OpenClaw at ${OPENCLAW_URL}`);
      const response = await axios.post(OPENCLAW_URL, {
        message: payload.text,
        user_id: payload.userId,
        session_id: id
      }, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 5000
      });
      openclawResponse = response.data;
      console.log(`[${new Date().toISOString()}] OpenClaw responded successfully`);
    } catch (error) {
      console.error(`[${new Date().toISOString()}] OpenClaw error: ${error.message}`);
    }
  }
  
  res.status(201).json({ 
    ok: true, 
    id, 
    status: task.status,
    openclawResponse 
  });
});

// Export router and tasks map for use in index.js
module.exports = { router, tasks };
