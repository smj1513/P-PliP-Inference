from app.services.agent_service import AgentService
from app.services.plan_service import PlanService


def get_agent_service():
    return AgentService()


def get_plan_service():
    return PlanService()
