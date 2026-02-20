# Dusty MVP End-to-End Test Report

**Test ID:** `dusty-end-to-end-test-1771596552`  
**Timestamp:** 2026-02-20T14:09:13+00:00  
**Status:** ⚠️ FAILED

## Component Health Check

| Component | Status | Response Time |
|-----------|--------|---------------|
| Telegram Bridge Mock | ❌ Failed | ms |
| Core-Agent | ✅ Healthy | 15ms |
| OpenClaw Mock | ✅ Healthy | 16ms |

## End-to-End Flow Tests

| Test | Status | Response Time |
|------|--------|---------------|
| POST /webhook (`/dust balance`) | ❌ Failed | 11ms |
| Dust Query (`Get my dust balance`) | ❌ Failed | 12ms |
| Core-Agent → OpenClaw Forward | ✅ Verified | - |

## Timing Summary

| Step | Time |
|------|------|
| Bridge Health Check | ms |
| Core-Agent Health Check | 15ms |
| OpenClaw Health Check | 16ms |
| E2E Webhook Test | 11ms |
| Dust Query Test | 12ms |
| **Total Execution Time** | **1113ms** |

## Results

- **Passed:** 2/5
- **Failed:** 3/5

Some tests failed. Check logs for details.
