from langchain_upstage import ChatUpstage
from app.core.config import settings

mini_llm = ChatUpstage(
    model=settings.UPSTAGE_MINI_MODEL,
    upstage_api_key=settings.UPSTAGE_API_KEY,
    temperature=0,
)

large_llm = ChatUpstage(
    model=settings.UPSTAGE_LARGE_MODEL,
    upstage_api_key=settings.UPSTAGE_API_KEY,
    temperature=0,
)
