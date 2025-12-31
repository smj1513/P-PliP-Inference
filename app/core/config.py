import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    # =========================================================
    # 1. 필수 변수 (타입만 지정하면 .env에서 없으면 에러 발생)
    # =========================================================

    # Qdrant 설정
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "attractions_hybrid"  # 기본값 지정 가능

    # Upstage 설정
    UPSTAGE_API_KEY: str
    UPSTAGE_LARGE_MODEL: str = "solar-pro2"
    UPSTAGE_MINI_MODEL: str = "solar-mini"

    # MySQL 설정
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str
    # =========================================================
    # 2. 선택 변수 (기본값을 주면 .env에 없어도 됨)
    # =========================================================

    # 모델명 관리 (코드 수정 없이 .env에서 모델 교체 가능하도록)
    DENSE_MODEL_QUERY: str = "embedding-query"
    DENSE_MODEL_PASSAGE: str = "embedding-passage"
    SPARSE_MODEL_NAME: str = "yjoonjang/splade-ko-v1"

    # 프로젝트 기본 설정
    PROJECT_NAME: str = "P-plip-inference"
    VERSION: str = "1.0.0"

    # Cohere 설정
    COHERE_API_KEY: str
    COHERE_MODEL: str = "rerank-multilingual-v3.0"

    # =========================================================
    # 3. 환경 설정 (.env 파일 로드 규칙)
    # =========================================================
    model_config = SettingsConfigDict(
        env_file=".env",  # 읽어올 파일명
        env_file_encoding="utf-8",  # 인코딩
        extra="ignore",  # .env에 정의되지 않은 키가 있어도 무시 (에러 방지)
    )


settings = Settings()
