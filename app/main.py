from app.core.llm_client import LLMClient
from app.db.database import Database
from app.db.retrieval import RetrievalSystem
from app.tools.router import Router
from app.tools.gift_finder import GiftFinderTool
from app.tools.support import SupportTool
from app.models.schemas import FinalResponse

class AgenticSystem:
    def __init__(self):
        self.llm = LLMClient()
        self.db = Database()
        # Seed data if empty is handled by the script now, but we can keep a check
        if not self.db.get_all_products():
            self.db.seed_data()
        
        self.retrieval = RetrievalSystem(self.db)
        self.router = Router(self.llm)
        self.gift_tool = GiftFinderTool(self.llm, self.retrieval)
        self.support_tool = SupportTool(self.llm)

    def handle_query(self, query: str) -> FinalResponse:
        route_decision = self.router.route(query)
        
        if route_decision.route == "gift_finder":
            output = self.gift_tool.process(query)
            return FinalResponse(
                route="gift_finder",
                output=output.dict(),
                response_en=output.response_en,
                response_ar=output.response_ar
            )
        else:
            output = self.support_tool.process(query)
            return FinalResponse(
                route="support",
                output=output.dict(),
                response_en=output.response_en,
                response_ar=output.response_ar
            )
