from fastapi import APIRouter
from app.core.dependencies import get_agent_service, get_plan_service
from app.services.agent_service import AgentService
from app.services.plan_service import PlanService
from fastapi import Depends
from app.api.v1.request.ai_request import SuggestRequest
from app.api.v1.response.ai_response import SuggestResponse
from typing import List
from app.api.v1.response.ai_response import PlanResponse
from app.api.v1.request.ai_request import PlanRequest

router = APIRouter()


@router.post("", response_model=List[SuggestResponse])
async def suggest_attraction(
    request: SuggestRequest, serivce: AgentService = Depends(get_agent_service)
):
    """
    사용자의 요청(query)을 받아 관광지를 추천합니다.
    """
    result = await serivce.suggest_attraction(request)
    return result


# -------------------------------------------------------------------
# 여행 계획 생성 API
# -------------------------------------------------------------------
@router.post("/plan", response_model=PlanResponse)
async def generate_travel_plan(
    request: PlanRequest, service: PlanService = Depends(get_plan_service)
):
    """
    사용자 테마와 선택한 관광지를 기반으로 여행 계획 생성
    """
    result = await service.generate_plan(
        request.user_theme, request.attraction_id, request.start_date, request.end_date
    )
    return result
