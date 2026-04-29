from app.core.llm_client import LLMClient
from app.models.schemas import RouterOutput

class Router:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def route(self, query: str) -> RouterOutput:
        prompt = f"""
        Classify the following user query into one of two categories: 'gift_finder' or 'support'.
        
        - 'gift_finder': Use this if the user is looking for product recommendations, gift ideas, or searching for specific items for babies/moms.
        - 'support': Use this if the user is asking about order status, refunds, complaints, delivery issues, or general customer service questions.
        
        User Query: "{query}"
        
        Output strictly in JSON format:
        {{
            "route": "gift_finder" or "support",
            "confidence": float (0-1),
            "reasoning": "short explanation"
        }}
        """
        
        result = self.llm.generate_json(prompt)
        if not result or "route" not in result:
            return RouterOutput(route="support", confidence=0.3, reasoning="Failed to classify, defaulting to support.")
        
        return RouterOutput(**result)
