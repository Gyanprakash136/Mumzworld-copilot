from app.core.llm_client import LLMClient
from app.models.schemas import SupportOutput

class SupportTool:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def process(self, query: str) -> SupportOutput:
        prompt = f"""
        You are a Customer Support Assistant for Mumzworld.
        Analyze the user query: "{query}"
        
        Classify into: order_status, refund, complaint, or general_query.
        Determine urgency (low, medium, high).
        Determine if it needs a human agent (refunds and complaints always need a human).
        Generate warm, helpful responses in English and Arabic.
        
        Output JSON:
        {{
            "intent": "order_status" | "refund" | "complaint" | "general_query",
            "urgency": "low" | "medium" | "high",
            "confidence": float,
            "reasoning": "short explanation",
            "needs_human": boolean,
            "response_en": "Natural English response...",
            "response_ar": "Natural Arabic response..."
        }}
        """
        
        result = self.llm.generate_json(prompt)
        
        if not result:
            return SupportOutput(
                intent="general_query",
                urgency="medium",
                confidence=0.5,
                reasoning="Failed to process, defaulting.",
                needs_human=True,
                response_en="I'm sorry, I'm having trouble processing your request. Let me connect you with a human agent.",
                response_ar="عذراً، أواجه مشكلة في معالجة طلبك. سأقوم بتحويلك إلى أحد موظفينا."
            )

        if result.get("intent") in ["refund", "complaint"]:
            result["needs_human"] = True
        if result.get("confidence", 1.0) < 0.6:
            result["needs_human"] = True

        return SupportOutput(**result)
