from app.agents.state import PlanState
from app.core.llm import mini_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

SEARCH_EVALUATION_PROMPT = ChatPromptTemplate.from_template(
    """
    [Role]
    You are a strict travel content evaluator. Your job is to assess whether the retrieved travel destinations match the user's requested theme.

    [Input]
    - User Theme: {user_theme}
    - Retrieved Destinations:
    {recommendations}

    [Criteria]
    1. **Relevance**: Do the destinations fit the theme? (e.g., if theme is "healing", are there parks/forests? if "history", are there palaces/museums?)
    2. **Diversity**: Is there a good mix of places? (Not critical, but good to have)
    
    [Task]
    - If the destinations are relevant to the theme, output "PASS".
    - If they are NOT relevant or very poor matches, output specific feedback on why they are bad and what kind of places should be searched instead.

    [Output Format (JSON)]
    {{
        "evaluation_result": "PASS" or "FAIL",
        "feedback": "Reason for failure and suggestion for better search terms" (leave empty if PASS)
    }}
    """
)


async def evaluate_search_node(state: PlanState) -> PlanState:
    user_theme = state["user_theme"]
    recommendations = state.get("recommendations", [])
    retry_count = state.get("retrieval_retry_count", 0)

    # 포맷팅
    rec_text = ""
    for idx, rec in enumerate(recommendations, 1):
        rec_text += f"{idx}. {rec.get('title')} ({rec.get('content_type')}) - {rec.get('overview', '')[:50]}\n"

    # LLM 평가
    chain = SEARCH_EVALUATION_PROMPT | mini_llm | JsonOutputParser()

    try:
        result = await chain.ainvoke(
            {"user_theme": user_theme, "recommendations": rec_text}
        )

        eval_result = result.get("evaluation_result", "PASS")
        feedback = result.get("feedback", "")

        if eval_result == "FAIL":
            return {
                "search_feedback": feedback,
                "retrieval_retry_count": retry_count + 1,
            }

        return {"search_feedback": "PASS"}

    except Exception as e:
        print(f"Error in search evaluation: {e}")
        # 에러 시 그냥 통과시킴 (무한 루프 방지)
        return {"search_feedback": "PASS"}
