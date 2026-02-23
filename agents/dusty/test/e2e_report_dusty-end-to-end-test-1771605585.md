# Dusty MVP End-to-End Test Report

**Test ID:** `dusty-end-to-end-test-1771605585`  
**Timestamp:** 2026-02-20T16:39:46+00:00  
**Status:** ⚠️ FAILED

## Component Health Check

| Component | Status | Response Time |
|-----------|--------|---------------|
| Telegram Bridge Mock | ❌ Failed | ms |
| Core-Agent | ✅ Healthy | 16ms |
| OpenClaw Mock | ✅ Healthy | 15ms |

## End-to-End Flow Tests

| Test | Status | Response Time |
|------|--------|---------------|
| POST /webhook (`/dust balance`) | ❌ Failed | 11ms |
| Dust Query (`Get my dust balance`) | ❌ Failed | 10ms |
| Core-Agent → OpenClaw Forward | ✅ Verified | - |

## Timing Summary

| Step | Time |
|------|------|
| Bridge Health Check | ms |
| Core-Agent Health Check | 16ms |
| OpenClaw Health Check | 15ms |
| E2E Webhook Test | 11ms |
| Dust Query Test | 10ms |
| **Total Execution Time** | **1100ms** |

## Results

- **Passed:** 2/5
- **Failed:** 3/5

Some tests failed. Check logs for details.
