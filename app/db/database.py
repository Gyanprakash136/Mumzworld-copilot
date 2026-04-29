import sqlite3
import json
import os
from typing import List, Dict

# Path to the canonical product dataset
PRODUCTS_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "products.json"
)

class Database:
    def __init__(self, db_path="data/mumzworld.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id         INTEGER PRIMARY KEY,
                name       TEXT    NOT NULL,
                category   TEXT,
                price_aed  REAL,
                tags       TEXT,       -- JSON-encoded list
                age_range  TEXT,
                description TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def seed_data(self):
        """Load all 100 products from data/products.json into SQLite."""
        with open(PRODUCTS_JSON_PATH, encoding="utf-8") as f:
            products = json.load(f)

        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM products")
        for p in products:
            conn.execute('''
                INSERT INTO products (id, name, category, price_aed, tags, age_range, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                p["id"],
                p["name"],
                p["category"],
                p["price_aed"],
                json.dumps(p["tags"]),   # store list as JSON string
                p["age_range"],
                p.get("description", "")
            ))
        conn.commit()
        conn.close()
        print(f"Seeded {len(products)} products into {self.db_path}")

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        d = dict(row)
        # Deserialize tags back to list
        try:
            d["tags"] = json.loads(d["tags"])
        except (TypeError, json.JSONDecodeError):
            d["tags"] = []
        return d

    def get_products_by_ids(self, ids: List[int]) -> List[Dict]:
        if not ids:
            return []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        placeholders = ", ".join(["?"] * len(ids))
        rows = conn.execute(
            f"SELECT * FROM products WHERE id IN ({placeholders})", ids
        ).fetchall()
        conn.close()
        return [self._row_to_dict(r) for r in rows]

    def get_all_products(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM products").fetchall()
        conn.close()
        return [self._row_to_dict(r) for r in rows]

    def filter_products(
        self,
        max_price: float = None,
        age_range: str = None,
        category: str = None,
        top_k: int = 10
    ) -> List[Dict]:
        """Structured filter for deterministic pre-filtering before vector search."""
        all_products = self.get_all_products()
        results = []
        for p in all_products:
            if max_price and p["price_aed"] > max_price:
                continue
            if category and category.lower() not in p["category"].lower():
                continue
            results.append(p)
        return results[:top_k]
