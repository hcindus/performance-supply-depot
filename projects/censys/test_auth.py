#!/usr/bin/env python3
"""
Censys Auth Test — Multiple Methods
Classification: OMEGA-LEVEL
"""

import requests
import base64

# Token details from Censys
api_secret = "censys_2V7HdW4u_FDMXcuZZp3819KQfWV9pYQyz"
api_id_attempts = [
    "Hcindus 2V7HdW4u",      # Token name
    "2V7HdW4u",              # Short code from name
    "Hcindus",               # Username only
    "censys_2V7HdW4u",       # From secret prefix
]

print("[CENSYS] Testing authentication methods...")
print(f"[CENSYS] Secret: {api_secret[:20]}...")

for api_id in api_id_attempts:
    print(f"\n[TEST] API ID: '{api_id}'")
    
    # Method 1: HTTP Basic Auth
    try:
        response = requests.get(
            "https://search.censys.io/api/v2/hosts/8.8.8.8",
            auth=(api_id, api_secret),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ SUCCESS! API ID = '{api_id}'")
            print(f"  Response: {response.json()}")
            exit(0)
        else:
            print(f"  ✗ {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n[FAIL] All auth attempts failed")
print("[INFO] Censys API requires API ID + Secret pair")
print("[INFO] Check https://search.censys.io/account for credentials")
