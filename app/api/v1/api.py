from fastapi import APIRouter
from app.api.v1.endpoints import suggest_router

api_router = APIRouter()

# 의도 분류 라우터 등록
# 태그는 'router' 또는 'classification' 등으로 지정
api_router.include_router(suggest_router.router, prefix="/suggest", tags=["suggest"])
