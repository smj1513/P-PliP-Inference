from pydantic import BaseModel, Field
from typing import List


class ContentTypeExtract(BaseModel):
    content_type: str  = Field(
        description="사용자의 질문에 가장 적합한 관광지 타입"
    )

# 평가 결과를 담을 Pydantic 구조 정의 (LLM 출력을 강제하기 위함)
class RelevanceScore(BaseModel):
    doc_id: int = Field(description="The index or ID of the document")
    score: float = Field(description="Relevance score between 0 and 100")

class RankedDocs(BaseModel):
    results: List[RelevanceScore]