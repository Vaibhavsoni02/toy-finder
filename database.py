import sqlite3
import json
from typing import List, Dict, Optional
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class ToyDatabase:
    def __init__(self, db_name: str = "toys.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the SQLite database"""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Create database tables"""
        print("📋 Creating database tables...")

        # Toys table
        self.cursor.execute("""
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
        """)

        # Images table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                toy_id TEXT,
                url TEXT,
                key TEXT,
                FOREIGN KEY (toy_id) REFERENCES toys(id)
            )
        """)

        # Facilitates (features/benefits) table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS facilitates (
                id TEXT PRIMARY KEY,
                name TEXT,
                image TEXT,
                is_archived INTEGER
            )
        """)

        # Toy facilitates junction table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS toy_facilitates (
                toy_id TEXT,
                facilitate_id TEXT,
                FOREIGN KEY (toy_id) REFERENCES toys(id),
                FOREIGN KEY (facilitate_id) REFERENCES facilitates(id),
                PRIMARY KEY (toy_id, facilitate_id)
            )
        """)

        self.conn.commit()
        print("✅ Database tables created successfully!")

    def import_from_json(self, json_file: str = "toys_data.json"):
        """Import toy data from JSON file"""
        print(f"📥 Importing data from {json_file}...")

        with open(json_file, 'r', encoding='utf-8') as f:
            toys_data = json.load(f)

        imported_count = 0

        for item in toys_data:
            toy = item.get('toy', {})
            if not toy:
                continue

            # Insert toy
            self.cursor.execute("""
                INSERT OR REPLACE INTO toys
                (id, name, price, short_description, slug, type, min_age, max_age, available_stock, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                toy.get('id'),
                toy.get('name'),
                toy.get('price'),
                toy.get('shortDescription'),
                toy.get('slug'),
                toy.get('type'),
                toy.get('ageGroup', {}).get('minAge'),
                toy.get('ageGroup', {}).get('maxAge'),
                item.get('availableStock', 0),
                item.get('createdAt')
            ))

            # Insert images
            for image in toy.get('images', []):
                self.cursor.execute("""
                    INSERT INTO images (toy_id, url, key)
                    VALUES (?, ?, ?)
                """, (toy.get('id'), image.get('url'), image.get('key')))

            # Insert facilitates and relationships
            for facilitate in toy.get('facilitates', []):
                facilitate_id = facilitate.get('id')

                # Insert facilitate if not exists
                self.cursor.execute("""
                    INSERT OR IGNORE INTO facilitates (id, name, image, is_archived)
                    VALUES (?, ?, ?, ?)
                """, (
                    facilitate_id,
                    facilitate.get('name'),
                    facilitate.get('image'),
                    1 if facilitate.get('isArchived') else 0
                ))

                # Create relationship
                self.cursor.execute("""
                    INSERT OR IGNORE INTO toy_facilitates (toy_id, facilitate_id)
                    VALUES (?, ?)
                """, (toy.get('id'), facilitate_id))

            imported_count += 1

        self.conn.commit()
        print(f"✅ Successfully imported {imported_count} toys into database!")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

class ToyFilter:
    def __init__(self, db_name: str = "toys.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def filter_toys(self,
                    min_age: Optional[int] = None,
                    max_age: Optional[int] = None,
                    min_price: Optional[float] = None,
                    max_price: Optional[float] = None,
                    search_text: Optional[str] = None,
                    toy_type: Optional[str] = None,
                    features: Optional[List[str]] = None,
                    limit: Optional[int] = None) -> List[Dict]:
        """
        Filter toys based on multiple criteria

        Args:
            min_age: Minimum age for child
            max_age: Maximum age for child
            min_price: Minimum price
            max_price: Maximum price
            search_text: Search in toy name or description
            toy_type: Toy type filter
            features: List of feature names to filter by
            limit: Maximum number of results
        """
        query = """
            SELECT DISTINCT t.*,
                   GROUP_CONCAT(DISTINCT f.name) as features
            FROM toys t
            LEFT JOIN toy_facilitates tf ON t.id = tf.toy_id
            LEFT JOIN facilitates f ON tf.facilitate_id = f.id
            WHERE 1=1
        """
        params = []

        # Age filter - child's age should be within toy's age range
        if min_age is not None:
            query += " AND t.min_age <= ?"
            params.append(min_age)

        if max_age is not None:
            query += " AND t.max_age >= ?"
            params.append(max_age)

        # Price filter
        if min_price is not None:
            query += " AND t.price >= ?"
            params.append(min_price)

        if max_price is not None:
            query += " AND t.price <= ?"
            params.append(max_price)

        # Search text filter
        if search_text:
            query += " AND (t.name LIKE ? OR t.short_description LIKE ?)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param])

        # Toy type filter
        if toy_type:
            query += " AND t.type = ?"
            params.append(toy_type)

        # Group by toy
        query += " GROUP BY t.id"

        # Feature filter (HAVING clause after GROUP BY)
        if features and len(features) > 0:
            feature_conditions = []
            for feature in features:
                feature_conditions.append("GROUP_CONCAT(DISTINCT f.name) LIKE ?")
                params.append(f"%{feature}%")
            query += " HAVING (" + " AND ".join(feature_conditions) + ")"

        # Order by price
        query += " ORDER BY t.price ASC"

        # Limit
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        # Convert to list of dictionaries
        toys = []
        for row in results:
            toy_dict = dict(row)

            # Fetch images for this toy
            self.cursor.execute("SELECT url, key FROM images WHERE toy_id = ?", (toy_dict['id'],))
            toy_dict['images'] = [dict(img) for img in self.cursor.fetchall()]

            toys.append(toy_dict)

        return toys

    def get_available_features(self) -> List[str]:
        """Get list of all available features"""
        self.cursor.execute("SELECT DISTINCT name FROM facilitates WHERE is_archived = 0 ORDER BY name")
        return [row['name'] for row in self.cursor.fetchall()]

    def get_price_range(self) -> tuple:
        """Get minimum and maximum prices"""
        self.cursor.execute("SELECT MIN(price) as min_price, MAX(price) as max_price FROM toys WHERE price IS NOT NULL")
        result = self.cursor.fetchone()
        return (result['min_price'], result['max_price'])

    def get_age_ranges(self) -> List[Dict]:
        """Get unique age ranges"""
        self.cursor.execute("""
            SELECT DISTINCT min_age, max_age
            FROM toys
            WHERE min_age IS NOT NULL AND max_age IS NOT NULL
            ORDER BY min_age, max_age
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_toy_types(self) -> List[str]:
        """Get all available toy types"""
        self.cursor.execute("SELECT DISTINCT type FROM toys WHERE type IS NOT NULL ORDER BY type")
        return [row['type'] for row in self.cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def setup_database():
    """Setup and populate the database"""
    db = ToyDatabase()
    db.connect()
    db.create_tables()
    db.import_from_json("toys_data.json")
    db.close()
    print("\n✨ Database setup complete!")

if __name__ == "__main__":
    setup_database()
