from langgraph.graph import StateGraph, END
from app.agents.state import PlanState
from app.agents.nodes import (
    load_attraction_node,
    rewrite_query_node,
    search_similar_attractions_node,
    search_accommodation_node,
    generate_plan_node,
    plan_review_node,
    evaluate_search_node,
)
from app.core.llm import mini_llm
from app.agents.prompts.templates import reranker_template
from app.schemas.chat_schema import RankedDocs
from langchain_core.output_parsers import PydanticOutputParser


def create_plan_graph():
    workflow = StateGraph(PlanState)

    # 노드 추가
    workflow.add_node("attraction_load", load_attraction_node)
    workflow.add_node("query_rewrite", rewrite_query_node)
    workflow.add_node("similar_search", search_similar_attractions_node)
    workflow.add_node("accommodation_search", search_accommodation_node)
    workflow.add_node("plan_generate", generate_plan_node)
    workflow.add_node("plan_review", plan_review_node)
    workflow.add_node("search_evaluator", evaluate_search_node)

    # 엣지 연결
    workflow.set_entry_point("attraction_load")
    workflow.add_edge("attraction_load", "query_rewrite")
    workflow.add_edge("query_rewrite", "similar_search")
    workflow.add_edge("similar_search", "search_evaluator")

    # 조건부 엣지 정의 (검색 평가 + 숙소 검색 여부)
    def check_search_and_trip_type(state: PlanState):
        # 1. 검색 품질 확인
        search_feedback = state.get("search_feedback", "PASS")
        retry_count = state.get("retrieval_retry_count", 0)

        # 재시도 필요 시 (단, retry_count < 3)
        if search_feedback != "PASS" and retry_count < 3:
            return "retry"

        # 2. 품질 통과(혹은 재시도 초과) 시 -> 일정 유형 확인
        start_date = state.get("start_date", "")
        end_date = state.get("end_date", "")

        if start_date and end_date and start_date == end_date:
            return "day_trip"

        return "overnight_trip"

    workflow.add_conditional_edges(
        "search_evaluator",
        check_search_and_trip_type,
        {
            "retry": "query_rewrite",
            "day_trip": "plan_generate",
            "overnight_trip": "accommodation_search",
        },
    )

    # accommodation_search -> plan_generate
    workflow.add_edge("accommodation_search", "plan_generate")
    workflow.add_edge("plan_generate", "plan_review")

    # 조건부 엣지 정의 (계획 검토)
    def should_continue(state: PlanState):
        review_feedback = state.get("review_feedback", "PASS")
        retry_count = state.get("retry_count", 0)

        if review_feedback == "PASS" or retry_count >= 3:
            return END
        return "plan_generate"

    workflow.add_conditional_edges(
        "plan_review",
        should_continue,
        {END: END, "plan_generate": "plan_generate"},
    )

    return workflow.compile()


app_graph = create_plan_graph()


# rerank_chain moved to app.agents.chains.py
