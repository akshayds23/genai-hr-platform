import httpx
import yaml


spec = yaml.safe_load(open('app/static/openapi.yaml'))
base_url = spec['servers'][0]['url'].rstrip('/')


print("=" * 60)
print("TEST 1: Login as superadmin")
print("=" * 60)
client1 = httpx.Client(base_url=base_url, timeout=30.0)
login_resp = client1.post('/api/login', json={'email': 'hr@example.com', 'password': 'hr123', 'role': 'hr'})
print(f"Login status: {login_resp.status_code}")
token = login_resp.json()['token']
print(f"Token: {token[:50]}...")


print("\n" + "=" * 60)
print("TEST 2: New client with Authentication-Token header")
print("=" * 60)
client2 = httpx.Client(base_url=base_url, timeout=30.0)
headers = {'Authentication-Token': token}
test_resp = client2.get('/api/hr/analytics/overview', headers=headers)
print(f"Status: {test_resp.status_code}")
print(f"Response: {test_resp.text[:200]}")


print("\n" + "=" * 60)
print("TEST 3: Same client that did login (has cookies)")
print("=" * 60)
test_resp2 = client1.get('/api/hr/analytics/overview', headers=headers)
print(f"Status: {test_resp2.status_code}")
print(f"Response: {test_resp2.text[:200]}")


print("\n" + "=" * 60)
print("TEST 4: Check cookies")
print("=" * 60)
print(f"Client1 cookies: {dict(client1.cookies)}")
print(f"Client2 cookies: {dict(client2.cookies)}")

client1.close()
client2.close()
