from fastapi import FastAPI
from app.api.v1.api import api_router
import uvicorn

from contextlib import asynccontextmanager
from app.db.vector_db import get_sparse_encoder


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    get_sparse_encoder()
    yield
    # Clean up the ML models and release the resources


app = FastAPI(
    title="P-plip Inference API",  # 1. 스웨거 상단 제목
    description="이 서비스는 관광지 추천 및 검색을 위한 AI 서버입니다.",  # 2. 상세 설명 (Markdown 지원)
    version="1.0.0",  # 3. API 버전
    # openapi_tags=tags_metadata,            # 4. 태그 설명 연결
    docs_url="/docs",  # 5. 스웨거 URL (기본값 /docs, 보안상 /api-docs 등으로 바꾸기도 함)
    redoc_url="/redoc",  # 6. ReDoc URL (또 다른 문서 뷰어)
    lifespan=lifespan,
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
