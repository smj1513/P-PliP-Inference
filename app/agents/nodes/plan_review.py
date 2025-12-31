from app.agents.state import PlanState


def plan_review_node(state: PlanState) -> PlanState:
    """
    생성된 계획을 검토하고 문제가 있다면 재시도를 위한 피드백을 생성합니다.
    """
    to_dos = state.get("to_dos", [])
    retry_count = state.get("retry_count", 0)

    # 1. 매칭되지 않은 항목 파악 (Attraction ID가 없거나 0인 경우)
    # create_plan_generate.py 로직을 보면 매칭 실패시 print하고 skip함.
    # 따라서 여기서는 'enriched_to_dos' 결과만 넘어오는데,
    # 만약 LLM이 5개를 생성했는데 여기 3개만 있다면 2개가 날아간 것임.
    # 하지만 원본 LLM 출력을 state에 저장하지 않으면 몇 개가 날아갔는지 알 수 없음.
    # 일단은 '내용이 너무 적거나', '필수 필드가 누락된' 경우를 체크.

    # 개선안: plan_generate에서 매칭 실패한 항목도 state에 'unmatched_items'로 넘겨주면 좋겠지만,
    # 현 단계에서는 'to_dos'가 비어있거나 너무 적은 경우를 체크.

    # 간단한 검증 로직:
    # 1. 아이템 개수가 0개면 무조건 재시도.
    # 2. (선택) 필수 필드 검사.

    if not to_dos:
        return {
            "review_feedback": "생성된 일정에 유효한 관광지가 없습니다. 추천 목록에 있는 명칭을 정확히 사용하여 다시 생성해주세요.",
            "retry_count": retry_count + 1,
        }

    # 성공 케이스
    return {"review_feedback": "PASS"}
