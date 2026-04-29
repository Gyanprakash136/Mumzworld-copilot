from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- Router Models ---
class RouterOutput(BaseModel):
    route: Literal["gift_finder", "support"]
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str

# --- Gift Finder Models ---
class Product(BaseModel):
    name: str
    category: str
    price_aed: float          # matches the real dataset field name
    tags: List[str]
    age_range: str
    description: Optional[str] = None
    reason: Optional[str] = None  # LLM-injected ranking reason

class GiftConstraints(BaseModel):
    budget: Optional[float] = None
    baby_age: Optional[str] = None
    intent: Optional[str] = None

class GiftFinderOutput(BaseModel):
    intent: str = "gift_finder"
    constraints: GiftConstraints
    recommendations: List[Product]
    confidence: float
    response_en: str
    response_ar: str

# --- Support Models ---
class SupportOutput(BaseModel):
    intent: Literal["order_status", "refund", "complaint", "general_query"]
    urgency: Literal["low", "medium", "high"]
    confidence: float
    reasoning: str
    needs_human: bool
    response_en: str
    response_ar: str

# --- Orchestrator Models ---
class FinalResponse(BaseModel):
    route: str
    output: dict  # holds either GiftFinderOutput or SupportOutput as dict
    response_en: str
    response_ar: str
