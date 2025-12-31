from app.agents.state import PlanState
from app.db.vector_db import search_hybrid
from app.db.filters import create_geo_radius_filter


async def search_similar_attractions_node(state: PlanState) -> PlanState:
    target = state["target_attraction"]
    user_theme = state["user_theme"]

    # 위치 필터 생성 (기본 10km)
    lat = target.get("latitude")
    lon = target.get("longitude")

    geo_filter = None
    if lat and lon:
        geo_filter = create_geo_radius_filter(lat=lat, lon=lon, radius_km=6.0)

    query_text = user_theme

    search_results = await search_hybrid(query=query_text, limit=5, filter=geo_filter)

    recommendations = []
    for res in search_results:
        recommendations.append(res)

    return {"recommendations": recommendations}
