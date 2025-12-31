from pydantic import BaseModel
from typing import Optional, Union, List
from pydantic import Field

class SuggestRequest(BaseModel):
    query: str
    content_types: Optional[Union[str, List[str]]] = None
    lat: float
    lng: float
    k: int
    m: int


class PlanRequest(BaseModel):
    user_theme: str = Field(description="사용자가 원하는 여행 테마")
    attraction_id: int = Field(description="중심이 되는 관광지의 ID")
    start_date:str = Field(description="여행 시작일 (YYYY-MM-DD)")
    end_date:str = Field(description="여행 종료일 (YYYY-MM-DD)")
