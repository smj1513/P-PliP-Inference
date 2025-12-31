from pydantic import BaseModel
from typing import List
from typing import Optional
from pydantic import Field

class SuggestResponse(BaseModel):
    no: int
    title: str
    content_type: str
    address: str
    latitude: float
    longitude: float
    big_image: str
    thumbnail: str
    tags: List[str] 
    homepage: str



class AttractionResponse(BaseModel):
    no: int
    title: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    addr1: Optional[str] = None
    overview: Optional[str] = None
    first_image1: Optional[str] = None
    first_image2: Optional[str] = None
    content_type: Optional[str] = None


class ToDoItem(BaseModel):
    name: str
    detail_plan_desc: str
    start_at: str  # datetime string
    end_at: str  # datetime string
    attraction: AttractionResponse


class PlanResponse(BaseModel):
    plan_title: str = Field(description="여행 계획의 제목")
    start_date: str = Field(description="여행 시작일 (YYYY-MM-DD)")
    end_date: str = Field(description="여행 종료일 (YYYY-MM-DD)")
    to_dos: List[ToDoItem]
