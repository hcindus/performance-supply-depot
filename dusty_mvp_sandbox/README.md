Dusty MVP Sandbox
=================
This folder contains the initial Node.js core agent, the Telegram mock bridge, and the OpenClaw mock, wired together for end-to-end testing of the Dusty MVP.

How to run:
- docker-compose up -d
- curl http://localhost:3000/status
- Use test-harness to trigger a sample task
- docker-compose down -v
