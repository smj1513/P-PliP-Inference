import json
from datetime import datetime
from app.agents.state import PlanState
from app.core.llm import mini_llm
from app.agents.prompts.plan_prompt import PLAN_GENERATE_PROMPT
from langchain_core.output_parsers import JsonOutputParser


async def generate_plan_node(state: PlanState) -> PlanState:
    user_theme = state["user_theme"]
    target = state["target_attraction"]
    start_date = state["start_date"]
    end_date = state["end_date"]
    recommendations = state.get("recommendations", [])
    accommodations = state.get("accommodations", [])

    # 추천 장소 목록 텍스트 변환
    rec_text = ""
    for idx, rec in enumerate(recommendations, 1):
        rec_text += f"{idx}. {rec.get('title')} ({rec.get('content_type')})\n"

    # 숙소 목록 텍스트 변환
    acc_text = ""
    for idx, acc in enumerate(accommodations, 1):
        acc_text += f"{idx}. {acc.get('title')} ({acc.get('content_type')})\n"

    review_feedback = state.get("review_feedback", "")
    retry_msg = ""
    if review_feedback and review_feedback != "PASS":
        retry_msg = f"\n\n[Previous Verification Feedback]\nThe previous plan had issues: {review_feedback}\nPlease fix these issues in the new plan."

    chain = PLAN_GENERATE_PROMPT | mini_llm | JsonOutputParser()

    result = await chain.ainvoke(
        {
            "user_theme": user_theme,
            "target_attraction_title": target["title"],
            "target_attraction_overview": target["overview"][:300] + "...",
            "recommendation_list": rec_text,
            "accommodation_list": acc_text,
            "start_date": start_date,
            "end_date": end_date,
            "feedback": retry_msg,
        }
    )

    # 1. 메타데이터 파싱
    plan_title = result.get("plan_title", "Custom Travel Plan")
    start_date = result.get("start_date", start_date)
    end_date = result.get("end_date", end_date)

    # 2. ToDo 아이템에 Attraction 정보 매핑 (Location 포함)
    enriched_to_dos = []

    # 검색 대상 리스트 (메인 관광지 + 추천 관광지 + 숙소)
    candidate_attractions = [target] + recommendations + accommodations

    for item in result.get("to_dos", []):
        todo_name = item.get("name", "")
        matched_attraction = None

        # 이름 매칭 (간단한 포함 관계)
        for attr in candidate_attractions:
            # LLM이 출력한 이름이 관광지 제목에 포함되거나 반대인 경우 매칭
            if todo_name.strip() in attr["title"] or attr["title"] in todo_name.strip():
                matched_attraction = attr
                break

        if matched_attraction:
            # 위치 정보 추출 로직 (MySQL vs VectorDB 구조 차이 대응)
            lat = matched_attraction.get("latitude")
            lon = matched_attraction.get("longitude")

            # VectorDB 결과인 경우 location 딕셔너리에 있을 수 있음 (MySQL은 바로 위 변수에 할당됨)
            if lat is None:
                loc = matched_attraction.get("location")
                if isinstance(loc, dict):
                    lat = loc.get("lat") or loc.get("latitude")
                    lon = loc.get("lon") or loc.get("longitude")

            attraction_data = {
                "no": matched_attraction.get("no") or 0,
                "title": matched_attraction.get("title") or todo_name,
                "latitude": float(lat) if lat is not None else None,
                "longitude": float(lon) if lon is not None else None,
                "addr1": matched_attraction.get("addr1"),
                "overview": matched_attraction.get("overview"),
                "first_image1": matched_attraction.get("first_image1"),
                "first_image2": matched_attraction.get("first_image2"),
                "content_type": matched_attraction.get("content_type"),
            }
        else:
            # 매칭 실패 시 결과에서 제외 (Hallucination 방지 및 DB 오류 방지)
            print(
                f"❌ Skipping invalid attraction: '{todo_name}' (Not found in candidates)"
            )
            continue

        item["attraction"] = attraction_data

        # ToDoItem 필수 필드 보장
        if "name" not in item:
            item["name"] = todo_name
        if "detail_plan_desc" not in item:
            item["detail_plan_desc"] = "상세 설명 없음"

        enriched_to_dos.append(item)

    return {
        "plan_title": plan_title,
        "start_date": start_date,
        "end_date": end_date,
        "to_dos": enriched_to_dos,
    }
