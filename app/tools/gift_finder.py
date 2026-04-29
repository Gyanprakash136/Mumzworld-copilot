from app.core.llm_client import LLMClient
from app.db.retrieval import RetrievalSystem
from app.models.schemas import GiftFinderOutput, GiftConstraints, Product

class GiftFinderTool:
    def __init__(self, llm: LLMClient, retrieval: RetrievalSystem):
        self.llm = llm
        self.retrieval = retrieval

    def process(self, query: str) -> GiftFinderOutput:
        # ── Step 1: Extract constraints ──────────────────────────────────────
        extraction_prompt = f"""
        Extract gift-finding constraints from the user query below.

        User Query: "{query}"

        Output ONLY valid JSON (no markdown):
        {{
            "budget": <float or null>,
            "baby_age": "<string describing age or null>",
            "intent": "<what the user is trying to achieve or null>"
        }}
        """
        # Groq / Llama-3.3-70B: fast, accurate JSON extraction
        constraints_data = self.llm.generate_json(extraction_prompt) or {}
        constraints = GiftConstraints(**constraints_data)

        # ── Step 2: Retrieve top-5 candidate products ────────────────────────
        retrieved = self.retrieval.search(query, top_k=5)
        if not retrieved:
            return GiftFinderOutput(
                constraints=constraints,
                recommendations=[],
                confidence=0.0,
                response_en="I couldn't find matching products. Please try rephrasing.",
                response_ar="لم أجد منتجات مناسبة. يرجى إعادة صياغة طلبك."
            )

        # Build a readable product catalogue for the LLM
        catalogue = "\n".join([
            f"[{i+1}] {p['name']} | {p['category']} | {p['price_aed']} AED"
            f" | Ages: {p['age_range']} | {p.get('description', '')}"
            for i, p in enumerate(retrieved)
        ])

        # ── Step 3: LLM ranks, reasons, and writes bilingual responses ────────
        recommendation_prompt = f"""
        You are a warm, expert gift advisor for Mumzworld, a premium UAE baby & mom store.

        User Query: "{query}"

        Available Products:
        {catalogue}

        Return ONLY valid JSON (no markdown) in this exact format:
        {{
            "recommendations": [
                {{
                    "name": "<exact product name from list>",
                    "category": "<category>",
                    "price_aed": <price as number>,
                    "tags": ["tag1", "tag2"],
                    "age_range": "<age range>",
                    "description": "<product description>",
                    "reason": "<1-sentence personalised reason why this fits the user's request>"
                }}
            ],
            "confidence": <float 0-1>,
            "response_en": "<2-3 sentence warm English response summarising your picks>",
            "response_ar": "<natural, warm Arabic response — NOT a literal translation>"
        }}

        Rules:
        - Recommend 1–3 products, prioritising budget if mentioned.
        - Only use products from the list above.
        - response_ar must read naturally in Gulf Arabic.
        """

        # Groq / Llama-3.3-70B: ranking, reasoning, and bilingual generation
        final = self.llm.generate_json(recommendation_prompt)
        if not final:
            return GiftFinderOutput(
                constraints=constraints,
                recommendations=[],
                confidence=0.2,
                response_en="I found products but couldn't rank them. Please try again.",
                response_ar="وجدت منتجات لكن لم أتمكن من ترتيبها. يرجى المحاولة مرة أخرى."
            )

        return GiftFinderOutput(
            constraints=constraints,
            recommendations=[Product(**r) for r in final.get("recommendations", [])],
            confidence=final.get("confidence", 0.75),
            response_en=final.get("response_en", ""),
            response_ar=final.get("response_ar", "")
        )
