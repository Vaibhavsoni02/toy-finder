"""
Migrate database by dropping and recreating tables with local_path column
"""
import json
import sqlite3
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Create new database with fresh name
import os
db_path = 'toys_new.db'

if os.path.exists(db_path):
    print(f"🗑️  Removing old toys_new.db...")
    try:
        os.remove(db_path)
        print("✅ Removed")
    except Exception as e:
        print(f"⚠️  Warning: {e}")

# Create new database
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

print("🗄️  Creating tables with local_path support...")

# Toys table
cursor.execute('''
    CREATE TABLE toys (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL,
        short_description TEXT,
        slug TEXT,
        type TEXT,
        min_age INTEGER,
        max_age INTEGER,
        available_stock INTEGER,
        created_at TEXT
    )
''')

# Images table with local_path
cursor.execute('''
    CREATE TABLE images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        toy_id TEXT NOT NULL,
        url TEXT,
        local_path TEXT,
        key TEXT,
        FOREIGN KEY (toy_id) REFERENCES toys(id)
    )
''')

# Facilitates table
cursor.execute('''
    CREATE TABLE facilitates (
        id TEXT PRIMARY KEY,
        name TEXT,
        image TEXT,
        is_archived INTEGER
    )
''')

# Junction table
cursor.execute('''
    CREATE TABLE toy_facilitates (
        toy_id TEXT,
        facilitate_id TEXT,
        PRIMARY KEY (toy_id, facilitate_id),
        FOREIGN KEY (toy_id) REFERENCES toys(id),
        FOREIGN KEY (facilitate_id) REFERENCES facilitates(id)
    )
''')

conn.commit()
print("✅ Tables created successfully!")

# Load data
print("📖 Loading data from toys_complete_with_local_images.json...")
with open('toys_complete_with_local_images.json', 'r', encoding='utf-8') as f:
    toys_data = json.load(f)

print(f"Found {len(toys_data)} toys to import")

for idx, toy_data in enumerate(toys_data, 1):
    toy = toy_data.get('toy', {})

    if not toy or not toy.get('id'):
        continue

    # Insert toy
    cursor.execute('''
        INSERT OR REPLACE INTO toys
        (id, name, price, short_description, slug, type, min_age, max_age, available_stock, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        toy['id'],
        toy.get('name'),
        toy.get('price'),
        toy.get('shortDescription'),
        toy.get('slug'),
        toy.get('type'),
        toy.get('minAge'),
        toy.get('maxAge'),
        toy.get('availableStock'),
        toy.get('createdAt')
    ))

    # Insert images with local paths
    for image in toy.get('images', []):
        local_path = image.get('local_path', '').replace('\\', '/')
        cursor.execute('''
            INSERT INTO images (toy_id, url, local_path, key)
            VALUES (?, ?, ?, ?)
        ''', (
            toy['id'],
            image.get('url'),
            local_path,
            image.get('key')
        ))

    # Insert facilitates
    for facilitate in toy.get('facilitates', []):
        if facilitate and facilitate.get('id'):
            cursor.execute('''
                INSERT OR IGNORE INTO facilitates (id, name, image, is_archived)
                VALUES (?, ?, ?, ?)
            ''', (
                facilitate['id'],
                facilitate.get('name'),
                facilitate.get('image'),
                facilitate.get('isArchived', 0)
            ))

            cursor.execute('''
                INSERT OR IGNORE INTO toy_facilitates (toy_id, facilitate_id)
                VALUES (?, ?)
            ''', (toy['id'], facilitate['id']))

    if idx % 100 == 0:
        print(f"  Processed {idx}/{len(toys_data)} toys...")

conn.commit()

# Show stats
cursor.execute('SELECT COUNT(*) FROM toys')
toy_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM images')
image_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM images WHERE local_path IS NOT NULL AND local_path != ""')
local_image_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM facilitates')
facilitate_count = cursor.fetchone()[0]

print("\n" + "="*60)
print("📊 DATABASE STATISTICS")
print("="*60)
print(f"Total toys: {toy_count}")
print(f"Total images: {image_count}")
print(f"Local images: {local_image_count}")
print(f"Failed/missing: {image_count - local_image_count}")
print(f"Unique features: {facilitate_count}")
print("="*60)

conn.close()
print("\n✅ Database successfully migrated with local image paths!")
