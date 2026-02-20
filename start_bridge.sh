#!/bin/bash
export CORE_AGENT_URL="http://localhost:3000/tasks"
cd /root/.openclaw/workspace/dusty_mvp_sandbox
node bridge_mock/bridge_mock.js
