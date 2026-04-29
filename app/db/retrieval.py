import os
import chromadb
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from app.db.database import Database

# ChromaDB persists to disk — no API key, no cloud, fully local
CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "chroma"
)
COLLECTION_NAME = "mumzworld-products"


class RetrievalSystem:
    def __init__(self, db: Database):
        self.db = db
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        # Persistent local ChromaDB client — creates data/chroma/ on first run
        self.client = PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # cosine similarity
        )

        # Auto-sync if collection is empty (first boot)
        if self.collection.count() == 0:
            print("🔄 ChromaDB empty — syncing products...")
            self.sync()
        else:
            print(f"✅ ChromaDB ready ({self.collection.count()} products indexed).")

    def _embed(self, text: str) -> list[float]:
        return self.encoder.encode(text).tolist()

    def _product_text(self, p: dict) -> str:
        """Rich text blob for embedding — covers all searchable fields."""
        tags = ", ".join(p["tags"]) if isinstance(p["tags"], list) else p.get("tags", "")
        return (
            f"{p['name']} {p['category']} {tags} "
            f"{p.get('description', '')} {p.get('age_range', '')}"
        ).strip()

    def sync(self):
        """
        Upsert all products from SQLite into ChromaDB.
        Safe to call multiple times — uses upsert semantics.
        """
        products = self.db.get_all_products()
        if not products:
            print("⚠️  No products in DB to sync.")
            return

        ids        = [str(p["id"]) for p in products]
        embeddings = [self._embed(self._product_text(p)) for p in products]
        documents  = [self._product_text(p) for p in products]
        metadatas  = [
            {
                "name":      p["name"],
                "category":  p["category"],
                "price_aed": float(p["price_aed"]),
                "age_range": p["age_range"],
            }
            for p in products
        ]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"✅ Synced {len(products)} products to ChromaDB at {CHROMA_PATH}")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Semantic search via ChromaDB → fetch full product rows from SQLite.
        Falls back to keyword scoring if ChromaDB returns nothing.
        """
        try:
            results = self.collection.query(
                query_embeddings=[self._embed(query)],
                n_results=min(top_k, self.collection.count()),
                include=["metadatas", "distances"]
            )
            ids = [int(i) for i in results["ids"][0]]
            if ids:
                return self.db.get_products_by_ids(ids)
        except Exception as e:
            print(f"⚠️  ChromaDB search error: {e}. Using keyword fallback.")

        # ── Local keyword fallback ────────────────────────────────────────────
        all_products = self.db.get_all_products()
        tokens = set(query.lower().split())

        scored = []
        for p in all_products:
            haystack = self._product_text(p).lower()
            score = sum(1 for t in tokens if t in haystack)
            if score > 0:
                scored.append((p, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in scored[:top_k]]
