from typing import TypedDict, List
from datetime import datetime


class PlanState(TypedDict):
    user_theme: str
    attraction_id: int
    target_attraction: "Attraction"
    recommendations: List["Attraction"]
    accommodations: List["Attraction"]
    plan_title: str
    start_date: str
    end_date: str
    to_dos: List["ToDo"]
    retry_count: int
    review_feedback: str
    retrieval_retry_count: int
    search_feedback: str


class ToDo(TypedDict):
    name: str
    detail_plan_desc: str
    start_at: datetime
    end_at: datetime
    attraction: "Attraction"


class Attraction(TypedDict):
    no: int
    content_id: int
    title: str
    content_type_id: int
    area_code: int
    si_gun_gu_code: int
    first_image1: str
    first_image2: str
    map_level: int
    latitude: float
    longitude: float
    tel: str
    addr1: str
    addr2: str
    homepage: str
    overview: str
    content_type: str
    tags: List[str]
