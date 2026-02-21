#!/usr/bin/env python3
"""
Censys Threat Intelligence — Auth Test
Classification: OMEGA-LEVEL
"""

import requests
import base64
import sys

api_secret = "censys_2V7HdW4u_FDMXcuZZp3819KQfWV9pYQyz"

print("[AUTH] Testing Censys API authentication...")

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Try with API secret only (some Censys v2 endpoints work this way)
print("\n[TEST 1] Using API Secret as Bearer token...")
headers["Authorization"] = f"Bearer {api_secret}"

try:
    response = requests.get("https://search.censys.io/api/v2/hosts/8.8.8.8", 
                          headers=headers, timeout=10)
    print(f"[STATUS] {response.status_code}")
    if response.status_code == 200:
        print("[SUCCESS] Bearer token auth works!")
        print(response.json()[:200])
    else:
        print(f"[FAIL] {response.text[:200]}")
except Exception as e:
    print(f"[ERROR] {e}")

# Try basic auth with empty username
print("\n[TEST 2] Using HTTP Basic Auth...")
del headers["Authorization"]
try:
    response = requests.get("https://search.censys.io/api/v2/hosts/8.8.8.8",
                          auth=("", api_secret),
                          headers=headers, timeout=10)
    print(f"[STATUS] {response.status_code}")
    if response.status_code == 200:
        print("[SUCCESS] Basic auth works!")
    else:
        print(f"[FAIL] {response.text[:200]}")
except Exception as e:
    print(f"[ERROR] {e}")

# Try search API directly
print("\n[TEST 3] Checking account status...")
try:
    response = requests.get("https://search.censys.io/api/v1/account",
                          headers={"Authorization": f"Bearer {api_secret}"},
                          timeout=10)
    print(f"[STATUS] {response.status_code}")
    if response.status_code == 200:
        print("[SUCCESS] Account API accessible!")
        print(response.text[:500])
    else:
        print(f"[FAIL] Check token permissions at censys.io")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n[COMPLETE] Auth tests finished")

