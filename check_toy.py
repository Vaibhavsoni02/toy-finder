import sqlite3
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('toys.db')
cursor = conn.cursor()

# Search for activity walker
cursor.execute("SELECT name, slug, type, price, min_age, max_age, short_description FROM toys WHERE slug = 'activity-walker'")
result = cursor.fetchone()

if result:
    print('=' * 60)
    print('✅ FOUND IN DATABASE!')
    print('=' * 60)
    print(f'Name: {result[0]}')
    print(f'Slug: {result[1]}')
    print(f'Type: {result[2]}')
    print(f'Price: ₹{result[3]}')
    print(f'Age: {result[4]//12}-{result[5]//12} years')
    print(f'Description: {result[6]}')
    print('=' * 60)
else:
    print('=' * 60)
    print('❌ NOT FOUND IN DATABASE')
    print('=' * 60)
    print('Toy slug "activity-walker" does not exist in our database.')
    print('This toy was likely not available during scraping (out of stock/unavailable).')
    print('\nThe EleFant website shows it exists, but it was not in the API response.')
    print('=' * 60)

conn.close()
