from app.agents.state import PlanState
from app.db.session import AsyncSessionLocal
from app.db.models import Attraction
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def load_attraction_node(state: PlanState) -> PlanState:
    attraction_id = state["attraction_id"]

    async with AsyncSessionLocal() as session:
        query = (
            select(Attraction)
            .options(selectinload(Attraction.tags))
            .where(Attraction.no == attraction_id)
        )
        result = await session.execute(query)
        attraction = result.scalar_one_or_none()

        if not attraction:
            raise ValueError(f"Attraction with id {attraction_id} not found")

        # ORM 객체를 TypedDict로 변환
        attraction_data = {
            "no": attraction.no,
            "content_id": attraction.content_id,
            "title": attraction.title,
            "content_type_id": attraction.content_type_id,
            "area_code": attraction.area_code,
            "si_gun_gu_code": attraction.si_gun_gu_code,
            "first_image1": attraction.first_image1,
            "first_image2": attraction.first_image2,
            "map_level": attraction.map_level,
            "latitude": float(attraction.latitude) if attraction.latitude else 0.0,
            "longitude": float(attraction.longitude) if attraction.longitude else 0.0,
            "tel": attraction.tel,
            "addr1": attraction.addr1,
            "addr2": attraction.addr2,
            "homepage": attraction.homepage,
            "overview": attraction.overview,
            "content_type": (
                attraction.content_type.value if attraction.content_type else None
            ),
            "tags": [tag.name for tag in attraction.tags],
        }

    return {"target_attraction": attraction_data}
