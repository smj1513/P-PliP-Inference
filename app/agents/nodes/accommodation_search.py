from sqlalchemy import select, func, and_
from app.agents.state import PlanState
from app.db.session import AsyncSessionLocal
from app.db.models import Attraction


async def search_accommodation_node(state: PlanState) -> PlanState:
    target = state["target_attraction"]

    # 위치 정보 (MySQL은 float, 없으면 0.0일 수 있음)
    lat = target.get("latitude")
    lon = target.get("longitude")

    accommodations = []

    if lat and lon:
        async with AsyncSessionLocal() as session:
            # 타겟 위치 포인트
            target_point = func.point(lon, lat)

            # 숙소 조회 쿼리: content_type_id=32 (숙박), 거리순 정렬, 상위 1개
            # MySQL ST_Distance_Sphere(g1, g2) -> g1, g2 Point(lon, lat)
            stmt = (
                select(Attraction)
                .where(
                    and_(
                        Attraction.content_type_id == 32,
                        Attraction.latitude.is_not(None),
                        Attraction.longitude.is_not(None),
                    )
                )
                .order_by(
                    func.st_distance_sphere(
                        func.point(Attraction.longitude, Attraction.latitude),
                        target_point,
                    )
                )
                .limit(1)
            )

            result = await session.execute(stmt)
            best_accommodation = result.scalar_one_or_none()

            if best_accommodation:
                # ORM 객체를 dict로 변환 (PlanState 호환)
                acc_data = {
                    "no": best_accommodation.no,
                    "title": best_accommodation.title,
                    "content_type": "숙박",
                    "content_type_id": 32,
                    "latitude": float(best_accommodation.latitude),
                    "longitude": float(best_accommodation.longitude),
                    "addr1": best_accommodation.addr1,
                    "overview": best_accommodation.overview,
                    "first_image1": best_accommodation.first_image1,
                    "first_image2": best_accommodation.first_image2,
                }
                accommodations.append(acc_data)

    return {"accommodations": accommodations}
