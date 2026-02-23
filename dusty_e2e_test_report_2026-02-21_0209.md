# Dusty MVP End-to-End Test Report

**Test Run:** Saturday, February 21st, 2026 — 2:09 AM (UTC)  
**Cron Job ID:** fdc63bd5-b2c2-481c-9a5f-d3e001eff52f  
**Test Status:** ⚠️ **PARTIAL SUCCESS**

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Result** | ⚠️ PARTIAL |
| **Health Checks Passed** | 3/3 (100%) |
| **Flow Tests Passed** | 1/3 (33%) |
| **Total Tests** | 6/6 executed |
| **Total Duration** | 53ms |

---

## Service Health Checks ✅

All three core services are healthy and operational:

| Service | Status | Latency | Uptime |
|---------|--------|---------|--------|
| **Telegram Bridge** | ✅ healthy | 13.52ms | 8h 43m |
| **Core-Agent** | ✅ healthy | 3.18ms | 59h 27m |
| **OpenClaw Mock** | ✅ healthy | 2.90ms | 10h 59m |

**Notes:**
- Core-Agent shows impressive uptime (59+ hours)
- OpenClaw Mock has processed **353 total interactions**
- Bridge has been stable for 8h 43m

---

## End-to-End Flow Tests

### Test 1: POST /webhook (Full E2E via Bridge) ⚠️ PARTIAL

**Test:** Send "/dust balance" via Bridge → Core-Agent → OpenClaw

| Metric | Value |
|--------|-------|
| **Status** | ⚠️ PARTIAL |
| **Latency** | 14.61ms |
| **Bridge → Core-Agent** | ✅ PASS |
| **Core-Agent → OpenClaw** | ❌ FAIL |

**Issue Identified:**
Core-Agent receives the request but fails to forward it properly to OpenClaw. The response shows:
```json
{
  "ok": true,
  "forwarded": true,
  "coreAgentResponse": {
    "ok": true,
    "id": "7e315ca1-e2b3-44cf-8c7a-3039470a3ad1",
    "status": "pending",
    "openclawResponse": { "bot": "dusty" }
  }
}
```

The response is being cut off, suggesting a potential timeout or error in the Core-Agent/OpenClaw communication.

---

### Test 2: dust-Specific Query ⚠️ PARTIAL

**Test:** "What is my dust balance?"

| Metric | Value |
|--------|-------|
| **Status** | ⚠️ PARTIAL |
| **Latency** | 7.01ms |
| **Core-Agent Processing** | ✅ Received |
| **OpenClaw Response** | ❌ Missing |

Same underlying issue as Test 1 - Core-Agent receives the query but OpenClaw response is missing.

---

### Test 3: Bridge GET /test Endpoint ✅ PASS

**Test:** Direct test endpoint on Bridge

| Metric | Value |
|--------|-------|
| **Status** | ✅ PASS |
| **Latency** | 8.65ms |
| **Mock Message Sent** | ✅ |
| **Core-Agent Reached** | ✅ |

This test passes because it likely uses a simpler code path that bypasses the OpenClaw forwarding issue.

---

## Timing Analysis

```
Service Health Checks:
  Bridge Health Check:      13.52ms
  Core-Agent Health Check:   3.18ms
  OpenClaw Health Check:     2.90ms
  ─────────────────────────────────
  Subtotal:                 19.60ms

End-to-End Tests:
  POST /webhook (E2E):       14.61ms
  Dust Query:                 7.01ms
  Bridge GET /test:           8.65ms
  ─────────────────────────────────
  Subtotal:                 30.27ms

═══════════════════════════════════
TOTAL TEST EXECUTION:       53ms
```

**Performance Notes:**
- All latency metrics are within acceptable thresholds (<100ms)
- Fastest service: OpenClaw mock (2.90ms health check)
- Bridge showing slightly higher latency (13.52ms) but still acceptable

---

## System State

- **353 total interactions** recorded by OpenClaw mock
- All services have healthy uptimes
- Core-Agent is the longest-running component (59h+ uptime)
- Bridge uptime: 8h 43m

---

## Issues Identified

### 🔴 Primary Issue: Core-Agent → OpenClaw Forwarding Failure

**Symptoms:**
- Health checks all pass (services are reachable)
- Core-Agent receives messages from Bridge successfully
- OpenClaw response is incomplete/cut off

**Likely Causes:**
1. Core-Agent to OpenClaw connection timeout
2. OpenClaw mock response format has changed
3. Network/configuration issue between Core-Agent and OpenClaw mock

**Recommended Actions:**
1. Check Core-Agent logs for forwarding errors
2. Verify OpenClaw mock response format
3. Test direct Core-Agent → OpenClaw POST request
4. Review `FORWARD_TO_AGENT_URL` configuration in Core-Agent

---

## Conclusion

The Dusty MVP pipeline has **partial functionality**. While all services are operational and responding to health checks, the critical end-to-end flow from Telegram → Bridge → Core-Agent → OpenClaw is **broken at the Core-Agent → OpenClaw step**.

**What's Working:**
- ✅ All service health checks
- ✅ Bridge → Core-Agent communication
- ✅ Bridge GET /test endpoint

**What's Broken:**
- ❌ Core-Agent → OpenClaw forwarding
- ❌ Full E2E dust queries

**Next Steps:**
1. Investigate Core-Agent forwarding logic
2. Check OpenClaw mock configuration
3. Verify network connectivity between Core-Agent and OpenClaw
4. Review recent changes to either component

---

**Report generated:** 2026-02-21T02:09:13Z  
**Test file:** `dusty_e2e_test_v2.js`

