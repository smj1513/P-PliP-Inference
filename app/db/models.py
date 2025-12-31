from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DECIMAL,
    ForeignKey,
    Enum,
    Table,
    DateTime,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base import Base

# Enum 타입 정의 (DB와 일치)
import enum


class ContentType(str, enum.Enum):
    ACCOMMODATION = "ACCOMMODATION"
    CULTURAL_FACILITY = "CULTURAL_FACILITY"
    FESTIVAL_PERFORMANCE_EVENT = "FESTIVAL_PERFORMANCE_EVENT"
    LEISURE_SPORTS = "LEISURE_SPORTS"
    SHOPPING = "SHOPPING"
    TOURIST_ATTRACTION = "TOURIST_ATTRACTION"
    TRAVEL_COURSE = "TRAVEL_COURSE"


# M:N 관계 테이블
attraction_tag_table = Table(
    "attraction_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("attraction_id", Integer, ForeignKey("attractions.no"), nullable=False),
    Column("tag_id", Integer, ForeignKey("tags.id"), nullable=False),
)


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class Attraction(Base):
    __tablename__ = "attractions"

    no: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="명소코드"
    )
    content_id: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="콘텐츠번호"
    )
    title: Mapped[str] = mapped_column(String(500), nullable=True, comment="명소이름")
    content_type_id: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="콘텐츠타입"
    )
    area_code: Mapped[int] = mapped_column(Integer, nullable=True, comment="시도코드")
    si_gun_gu_code: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="구군코드"
    )
    first_image1: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="이미지경로1"
    )
    first_image2: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="이미지경로2"
    )
    map_level: Mapped[int] = mapped_column(Integer, nullable=True, comment="줌레벨")
    latitude: Mapped[float] = mapped_column(
        DECIMAL(20, 17), nullable=True, comment="위도"
    )
    longitude: Mapped[float] = mapped_column(
        DECIMAL(20, 17), nullable=True, comment="경도"
    )
    tel: Mapped[str] = mapped_column(String(20), nullable=True, comment="전화번호")
    addr1: Mapped[str] = mapped_column(String(100), nullable=True, comment="주소1")
    addr2: Mapped[str] = mapped_column(String(100), nullable=True, comment="주소2")
    homepage: Mapped[str] = mapped_column(
        String(1000), nullable=True, comment="홈페이지"
    )
    overview: Mapped[str] = mapped_column(Text, nullable=True)
    area_code_id: Mapped[int] = mapped_column(Integer, nullable=True)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), nullable=True)

    # Relationship
    tags = relationship("Tags", secondary=attraction_tag_table, lazy="selectin")
