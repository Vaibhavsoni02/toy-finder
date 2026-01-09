"""
Updated database.py to use local image paths instead of CDN URLs
"""
import json
import sqlite3
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class ToyDatabase:
    def __init__(self, db_name: str = 'toys.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Create all necessary tables"""

        # Toys table - store main toy information
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS toys (
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

        # Images table - store image URLs AND local paths
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                toy_id TEXT NOT NULL,
                url TEXT,
                local_path TEXT,
                key TEXT,
                FOREIGN KEY (toy_id) REFERENCES toys(id)
            )
        ''')

        # Facilitates table - store unique features/facilitates
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS facilitates (
                id TEXT PRIMARY KEY,
                name TEXT,
                image TEXT,
                is_archived INTEGER
            )
        ''')

        # Junction table for many-to-many relationship
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS toy_facilitates (
                toy_id TEXT,
                facilitate_id TEXT,
                PRIMARY KEY (toy_id, facilitate_id),
                FOREIGN KEY (toy_id) REFERENCES toys(id),
                FOREIGN KEY (facilitate_id) REFERENCES facilitates(id)
            )
        ''')

        self.conn.commit()

    def clear_tables(self):
        """Clear all tables"""
        self.cursor.execute('DELETE FROM toy_facilitates')
        self.cursor.execute('DELETE FROM images')
        self.cursor.execute('DELETE FROM facilitates')
        self.cursor.execute('DELETE FROM toys')
        self.conn.commit()

    def insert_toy(self, toy_data):
        """Insert a single toy with all its data"""
        toy = toy_data.get('toy', {})

        if not toy or not toy.get('id'):
            return

        # Insert toy basic info
        self.cursor.execute('''
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
            local_path = image.get('local_path', '').replace('\\', '/')  # Normalize path
            self.cursor.execute('''
                INSERT INTO images (toy_id, url, local_path, key)
                VALUES (?, ?, ?, ?)
            ''', (
                toy['id'],
                image.get('url'),
                local_path,
                image.get('key')
            ))

        # Insert facilitates and relationships
        for facilitate in toy.get('facilitates', []):
            if facilitate and facilitate.get('id'):
                # Insert facilitate (will be ignored if exists)
                self.cursor.execute('''
                    INSERT OR IGNORE INTO facilitates (id, name, image, is_archived)
                    VALUES (?, ?, ?, ?)
                ''', (
                    facilitate['id'],
                    facilitate.get('name'),
                    facilitate.get('image'),
                    facilitate.get('isArchived', 0)
                ))

                # Insert relationship
                self.cursor.execute('''
                    INSERT OR IGNORE INTO toy_facilitates (toy_id, facilitate_id)
                    VALUES (?, ?)
                ''', (toy['id'], facilitate['id']))

    def load_from_json(self, json_file: str = 'toys_with_local_images.json'):
        """Load data from JSON file with local image paths"""
        print(f"📖 Loading data from {json_file}...")

        with open(json_file, 'r', encoding='utf-8') as f:
            toys_data = json.load(f)

        print(f"Found {len(toys_data)} toys")

        for idx, toy_data in enumerate(toys_data, 1):
            self.insert_toy(toy_data)
            if idx % 100 == 0:
                print(f"Processed {idx}/{len(toys_data)} toys...")

        self.conn.commit()
        print(f"✅ Successfully loaded {len(toys_data)} toys!")

    def get_stats(self):
        """Print database statistics"""
        self.cursor.execute('SELECT COUNT(*) FROM toys')
        toy_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM images')
        image_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM images WHERE local_path IS NOT NULL AND local_path != ""')
        local_image_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM facilitates')
        facilitate_count = self.cursor.fetchone()[0]

        print("\n" + "="*60)
        print("📊 DATABASE STATISTICS")
        print("="*60)
        print(f"Total toys: {toy_count}")
        print(f"Total images: {image_count}")
        print(f"Local images: {local_image_count}")
        print(f"Failed/missing: {image_count - local_image_count}")
        print(f"Unique features: {facilitate_count}")
        print("="*60)

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Create database
    db = ToyDatabase('toys.db')
    db.connect()

    print("🗄️  Creating tables...")
    db.create_tables()

    print("🧹 Clearing existing data...")
    db.clear_tables()

    # Load data
    db.load_from_json('toys_with_local_images.json')

    # Show stats
    db.get_stats()

    db.close()
    print("\n✅ Database ready with local image paths!")
