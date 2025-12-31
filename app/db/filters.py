from qdrant_client.http import models
from langchain_core.documents import BaseDocumentTransformer, Document
from typing import Sequence, Any

class PlaceIdDeduplicator(BaseDocumentTransformer):
    """메타데이터의 'no' 필드를 기준으로 중복 장소를 제거합니다."""
    def transform_documents(self, documents: Sequence[Document], **kwargs: Any) -> Sequence[Document]:
        unique_docs = []
        seen_ids = set()
        for doc in documents:
            # no가 없으면 title을, 그것도 없으면 본문을 ID로 사용
            place_id = doc.metadata.get("no") or doc.metadata.get("title") or doc.page_content
            if place_id not in seen_ids:
                unique_docs.append(doc)
                seen_ids.add(place_id)
        return unique_docs

def create_geo_radius_filter(
    lat: float, lon: float, radius_km: float = 10.0
) -> models.Filter:
    """
    주어진 좌표(lat, lon) 반경 radius_km 이내의 데이터를 검색하기 위한 Qdrant Filter를 생성합니다.
    """
    return models.Filter(
        must=[
            models.FieldCondition(
                key="location",
                geo_radius=models.GeoRadius(
                    center=models.GeoPoint(lon=lon, lat=lat),
                    radius=radius_km * 1000,  # km to meters
                ),
            )
        ]
    )


from typing import Optional, Union, List


def build_geo_fileter(lat: float, lon: float, radius_m: int = 1000) -> models.Filter:
    """
    중심 좌표(lat,lon)로 부터 반경 내의 데이터만 필터링 하는 조건 생성
    """
    return models.Filter(
        must=[
            models.FieldCondition(
                key="location",
                geo_radius=models.GeoRadius(
                    center=models.GeoPoint(lat=lat, lon=lon), radius=radius_m
                ),
            ),
        ]
    )


def build_geo_fileter_with_content_type(
    lat: float,
    lon: float,
    radius_m: int = 1000,
    content_type: Optional[Union[str, List[str]]] = None,
) -> models.Filter:
    """
    중심 좌표(lat,lon)로 부터 반경 내 + 특정 컨텐츠 타입 데이터만 필터링
    """
    # 1. 기본 지리적 필터 생성
    geo_filter = build_geo_fileter(lat, lon, radius_m)
    if content_type:
        match_condition = None

        # [수정 2] 리스트인 경우 OR 조건(MatchAny) 사용
        if isinstance(content_type, list):
            # SQL의 IN (...) 과 동일하게 동작: ["관광지", "음식점"] 중 하나면 통과
            match_condition = models.MatchAny(any=content_type)

        # [수정 3] 문자열인 경우 기존대로 단일 일치(MatchValue) 사용
        else:
            match_condition = models.MatchValue(value=content_type)

        # 4. 조건 생성 및 추가
        content_condition = models.FieldCondition(
            key="content_type", match=match_condition
        )

        # 3. 기존 필터의 must 리스트에 추가
        # (append는 반환값이 None이므로, return 문에서 바로 쓰면 안 됩니다)
        geo_filter.must.append(content_condition)

    # 4. 수정된 필터 객체 반환
    return geo_filter


