from enum import Enum

# 단순 리스트 대신 Enum 클래스 사용
class ContentTypes(str, Enum):
    TOURIST_SPOT = "관광지"
    CULTURE = "문화시설"
    FESTIVAL = "축제공연행사"
    COURSE = "여행코스"
    LEPORTS = "레포츠"
    STAY = "숙박"
    SHOPPING = "쇼핑"
    FOOD = "음식점"