# GitHub Messaging Skill

## Overview
Fallback communication via GitHub commits when direct connections fail.

## Capabilities
- Polls GitHub for new messages
- Pushes updates to remote repos
- Works as backup communication channel
- Supports multiple repositories

## Usage

### Start Poller
```bash
node poller.js &
```

### Send Message via GitHub
```bash
# Write message to memory/message.md
echo "# Message" > memory/message.md
git add memory/message.md
git commit -m "MESSAGE: Your message here"
git push origin main
```

### Configuration
Edit poller.js to set:
- WORKSPACE - Path to workspace
- POLL_INTERVAL - Check frequency (default: 60000ms)
- REPO_URL - Remote repository to poll

## How It Works
1. Poller checks remote for new commits
2. Pulls changes if new commits found
3. Reads messages from memory/message.md
4. Can trigger responses via commits

## Notes
- 60 second delay by default
- Works even when tunnels are down
- Use for critical messages as backup
