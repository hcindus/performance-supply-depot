#!/usr/bin/env python3
"""
Censys API Authentication Test v2
Account: 100 credits, Limited Lookup APIs
Token: censys_2V7HdW4u_FDMXcuZZp3819KQfWV9pYQyz
"""

import requests
import base64

# The token/credentials from your dashboard
token = "censys_2V7HdW4u_FDMXcuZZp3819KQfWV9pYQyz"

# Try Bearer token with explicit API endpoint
print("[CENSYS] Testing with Bearer token...")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Target: Singapore cluster IPs
test_ip = "165.245.143.157"  # Our recidivist

# Try v2 hosts endpoint
url = f"https://search.censys.io/api/v2/hosts/{test_ip}"

print(f"[QUERY] {test_ip}")
print(f"[AUTH] Bearer token: {token[:20]}...")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"[STATUS] {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ AUTHENTICATION SUCCESS!")
        print(f"\n[RESULTS]")
        print(f"  IP: {data.get('ip')}")
        print(f"  Last Updated: {data.get('last_updated_at')}")
        
        services = data.get('services', [])
        print(f"  Services: {len(services)}")
        for svc in services[:5]:
            print(f"    - Port {svc.get('port')}: {svc.get('service_name', 'unknown')}")
            
        # ASN
        asn = data.get('autonomous_system', {})
        print(f"\n[ASN] AS{asn.get('asn')} - {asn.get('name')}")
        
        # Location
        loc = data.get('location', {})
        print(f"\n[LOCATION]")
        print(f"  City: {loc.get('city')}")
        print(f"  Country: {loc.get('country')}")
        print(f"  Coordinates: {loc.get('coordinates', {}).get('latitude')}, {loc.get('coordinates', {}).get('longitude')}")
        
    elif response.status_code == 401:
        print("❌ Authentication failed")
        print(f"Response: {response.text}")
    elif response.status_code == 403:
        print("❌ Forbidden - API permissions issue")
        print(f"Response: {response.text}")
        print("\n[NOTE] Limited Lookup APIs may require different endpoint")
    elif response.status_code == 404:
        print(f"📍 IP not in Censys database")
    else:
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[COMPLETE]")
