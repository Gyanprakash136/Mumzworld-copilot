import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import Database
from app.db.retrieval import RetrievalSystem

def seed():
    print("=== Mumzworld DB + ChromaDB Seed ===")

    # 1. Seed SQLite from products.json
    db = Database()
    db.seed_data()

    # 2. Sync embeddings to ChromaDB (local, no API key)
    print("Syncing embeddings to ChromaDB...")
    retrieval = RetrievalSystem(db)
    retrieval.sync()

    print("\n✅ All done! System is ready.")
    print(f"   SQLite  → data/mumzworld.db  ({len(db.get_all_products())} products)")
    print(f"   ChromaDB → data/chroma/       ({retrieval.collection.count()} vectors)")

if __name__ == "__main__":
    seed()
