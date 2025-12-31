from app.agents.graph import app_graph


class PlanService:
    async def generate_plan(self, user_theme: str, attraction_id: int, start_date: str, end_date: str) -> dict:
        inputs = {"user_theme": user_theme, "attraction_id": attraction_id, "start_date": start_date, "end_date": end_date}

        # LangGraph 실행
        result = await app_graph.ainvoke(inputs)

        # 결과 반환 (PlanState의 전체 메타데이터 및 to_dos)
        return {
            "plan_title": result.get("plan_title", "My Travel Plan"),
            "start_date": result.get("start_date", ""),
            "end_date": result.get("end_date", ""),
            "to_dos": result.get("to_dos", []),
        }
