from app.agents.state import PlanState
from app.core.llm import mini_llm
from app.agents.prompts.query_rewrite_prompt import QUERY_REWRITE_PROMPT
from langchain_core.output_parsers import StrOutputParser


async def rewrite_query_node(state: PlanState) -> PlanState:
    user_theme = state["user_theme"]
    target = state["target_attraction"]

    chain = QUERY_REWRITE_PROMPT | mini_llm | StrOutputParser()

    search_feedback = state.get("search_feedback", "")
    feedback_msg = ""
    if search_feedback and search_feedback != "PASS":
        feedback_msg = f"\n[Previous Search Feedback]\nThe previous search failed because: {search_feedback}\nPlease generate a different query to address this issue."

    new_query = await chain.ainvoke(
        {
            "user_theme": user_theme,
            "target_attraction_title": target["title"],
            "target_attraction_overview": target["overview"][:300],  # 너무 길면 자름
            "feedback": feedback_msg,
        }
    )

    return {"user_theme": new_query}
