import sqlite3
import requests
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('toys.db')
cursor = conn.cursor()

# Get first image URL
cursor.execute('SELECT t.name, i.url FROM toys t JOIN images i ON t.id = i.toy_id LIMIT 1')
result = cursor.fetchone()

if result:
    toy_name, url = result
    print(f"Testing image for: {toy_name}")
    print(f"URL: {url[:100]}...")

    try:
        response = requests.head(url, timeout=5)
        print(f"\nHTTP Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Image URL is working!")
        elif response.status_code == 403:
            print("❌ Image URL has EXPIRED (403 Forbidden)")
            print("\nThe URLs have expiration tokens and are no longer valid.")
            print("This is normal for CDN signed URLs.")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing URL: {e}")

conn.close()
