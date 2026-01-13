# P-PliP ( P 성향 여행자를 위한 즉흥 여행 도우미 )

## 개요

### 시스템의 목표
본 프로젝트는 **'계획은 귀찮지만, 효율적인 여행은 하고 싶은'** P(인식형) 성향의 여행자들을 위한 즉흥 여행 추천 및 보조 웹 어플리케이션입니다.

기존의 여행 플랫폼들이 J(판단형) 성향의 '철저한 계획 수립'에 초점을 맞춘 것과 달리, P-PliP은 사용자의 모호한 니즈를 파악하여 **Just-in-Time (적시)** 정보를 제공하고, 선택의 스트레스를 최소화하는 것을 목표로 합니다.

- **Dual Recommendation Flow**: '극단적 P'를 위한 즉각적 장소 추천과 '중도적 P'를 위한 유연한 계획 생성을 모두 지원합니다.
- **Zero-Burden Planning**: 복잡한 검색 없이 대화형 인터페이스(Chatbot)로 여행 코스를 제안받습니다.
- **Dynamic Exploration**: 지도 기반의 직관적인 탐색과 실시간 위치 기반 추천을 제공합니다.

### 페르소나 및 문제 해결
*   **김지수 (Extreme P)**: "지금 당장 갈 곳 하나만 알려줘." -> **단일 장소/리스트 즉시 추천**
*   **이준영 (Moderate P)**: "큰 틀은 정해졌는데, 세부는 귀찮아." -> **관심 장소 선택 시 연계 코스 자동 생성**

<br>

## 프로젝트 구조
<img width="593" height="650" alt="image" src="https://github.com/user-attachments/assets/fcabc4c9-928a-479b-97b7-1b38f05e2460" />
<br>

## 기여 내용 및 트러블 슈팅

* 관광지 추천 엔진 구현 및 추천 성능 고도화
* LangGraph 기반 여행 계획 자동 생성 에이전트 구성
* JWT기반 인증 시스템 구축
* Web Application CRUD API 전반 설계 및 구현

### 1. 관광지 추천 엔진 구현 및 성능 고도화
#### 성과 : 추천 성능 20% 개선

#### 최종 완성된 관광지 추천 흐름도
<img width="743" height="345" alt="image" src="https://github.com/user-attachments/assets/298a1a51-11ba-4ff6-a6da-009cf4446ac4" />


#### 1.1. 추천 엔진 평가 지표 수립 및 기존 지표의 한계점
'관광지 추천' 기능에서 실제 사용시에 사용자가 원하는 장소와 다른 유형의 장소가 추천되는 문제점이 있었습니다. (ex, 카페 검색시 카페가 아닌 음식점이 추천됨) 이 문제를 해결하기 위해 실질적으로 사용자에게 필요한 '어떤 장소가 원하는 니즈와 가장 잘 부합하는가'를 판단하는 지표를 세우며 이를 추적하며 성능을 개선할 필요성이 있었습니다.

초기에는 검색 엔진의 성능을 측정하기 위해 전통적인 정보 검색 지표인 **NDCG**와 **Hit Rate**를 사용했습니다. 그러나 실제 관광지 검색 실험 결과, 다음 세 가지 이유로 해당 지표들이 우리 프로젝트에서 성능을 직접적으로 반영하지 못함을 깨달았습니다.

1. **도메인이 명확하지 않은** 작업에서의 추천 성능:
우리 시스템에서 목표로 하는 것은 사용자에게 '어떤 장소가 원하는 니즈와 가장 잘 부합하는가'를 판단하는 것 입니다. 이는 기술 문서나 구조화된 문서에 대한 검색 처럼 특정한 질문에 명확한 정답이 있는 태스크가 아닙니다. 'Open Domain'에 가까운 형태의 태스크였기 때문에 기존 평가 지표와는 다른 차별화된 기준점이 필요했습니다.

2. **정답(Ground Truth)의 모호성**: "분위기 좋은 카페"를 검색했을 때, 특정 A 카페만이 정답이 아닙니다. B, C 카페도 사용자의 의도에 부합한다면 정답으로 인정되어야 합니다. 기존 지표는 미리 정의된 특정 문서 하나만 정답으로 간주하여 성능을 과소평가했습니다.

3. **순위보다 중요한 '포함 여부'**: 지도 기반 추천 특성상, 1위와 5위의 순서 차이보다는 "사용자가 원하는 유형의 장소가 결과 리스트에 얼마나 잘 포함되어 있는가"가 더 중요했습니다.

#### 1.2. LLM as Judge (RAGAS) 도입과 커스텀 평가 기준 수립
이에 따라 LLM을 심판(Judge)으로 활용하여 검색 결과의 '질적 적합성'을 평가하는 **RAGAS(Retrieval Augmented Generation Assessment)** 프레임워크를 도입했습니다. 특히 우리 프로젝트에 특화된 두 가지 커스텀 메트릭을 설계했습니다.

**① Category Alignment (카테고리 일치성)**
사용자가 원하는 장소 유형(예: 카페, 식당, 공원)이 검색 결과의 '지배적인 정체성'과 일치하는지 엄격히 판단합니다. Dense 검색에서 흔히 발생하는 '연관성 오류'(예: "해변 뷰가 좋은 카페 추천해줘" 라는 쿼리에 대해 "뷰가 좋은 파인다이닝 레스토랑" 추천)를 걸러냅니다.

<details>
<summary>평가 프롬프트 (Category Alignment)</summary>

```python
category_alignment = AspectCritic(
    name="category_alignment",
    definition="""
    [Role]
    You are a 'Tourism Data Inspector' who has a perfect understanding of the classification system for 8 types of tourism (Tourist Attractions, Cultural Facilities, Festivals/Performances/Events, Travel Courses, Leisure/Sports, Accommodations, Shopping, and Restaurants).

    [Definition of Evaluation Categories]
    - Tourist Attractions: Places for sightseeing such as natural landscapes, historical sites, and parks.
    - Cultural Facilities: Facility-based cultural activities such as museums, art galleries, performance halls, and libraries.
    - Festivals/Performances/Events: Festivals or events held during a specific period.
    - Travel Courses: Recommended routes connecting multiple points.
    - Leisure/Sports: Activity and experience-centered locations such as surfing, skiing, and bungee jumping.
    - Accommodations: Places to stay overnight such as hotels, guesthouses, and campsites.
    - Shopping: Places for purchasing goods such as markets, duty-free shops, and souvenir shops.
    - Restaurants: Places for dining and drinking such as restaurants, cafes, and bakeries.

    [Evaluation Criteria: Strict Prohibition of Category Violation]
    1. First, identify the 'Target Type' explicitly stated or implied by the questioner.
    2. If the 'Dominant Identity' of the retrieved document differs from that type, it is immediately 0 points.
    3. Detect 'Association Errors' typical of Dense searches.
       - Example: If searching for "Accommodation with a sea view," a "Cafe with a sea view (Restaurant)" or "Sea Observatory (Tourist Attraction)" is 0 points.
       - Example: If searching for "Traditional Craft Shopping," a "Traditional Museum (Cultural Facility)" is 0 points.
    4. Ancillary facilities are not the primary identity. A restaurant inside a hotel is classified as 'Accommodation,' not a 'Restaurant.'

    [Scoring]
    - 1 point: The primary identity of the place perfectly matches the user's target type.
    - 0 points: The types are different, or a place of a different type was recommended simply because it has a 'similar vibe.'

    Let's think step by step.
    """,
    strictness=3
)
```
</details>

**② Vibe Relevance (분위기/조건 적합성)**
사용자의 추상적인 요구사항(예: "조용한", "야경이 예쁜", "주차 가능한")이 검색된 장소 설명(Overview)에 **명시적 근거**로 존재하는지 체크합니다. 또한, "조용한"을 검색했을때, "시끌벅적한"과 같은 반대 성향의 의미를 가진 설명을 걸러냅니다.

<details>
<summary>평가 프롬프트 (Vibe Relevance)</summary>

```python
vibe_relevance = AspectCritic(
    name="vibe_relevance",
    definition="""
    [Role]
    You are a 'Fact-Check Investigator' who verifies whether the user's requirements are explicitly stated in the document's text.

    [Evaluation Guidelines: Inference and Imagination Prohibited]
    1. Verify whether the constraints included in the question exist as explicit evidence within the document.
    2. Exclude your subjective common sense. Do not assume "It must be educational because it's a museum" or "The air must be fresh because it's a mountain." If the document does not describe those specific characteristics, it is 0 points.
    3. Even if the category is correct, if the detailed conditions differ, it is 0 points. (e.g., The user wants a 'quiet tourist attraction' but an 'active theme park' is retrieved.)

    [Passing Criteria: 1 point]
    - Specific descriptions or keywords supporting the atmosphere/conditions of the question actually exist in the document.
    [Failing Criteria: 0 points]
    - If the characteristics cannot be confirmed based solely on the document content.
    - If the actual nature of the place conflicts with the user's intent.

    Let's think step by step.
    """,
    strictness=3
)
```
</details>

#### 1.3. 실험 설계: Open Domain 평가 데이터셋 구축
기존의 "특정 장소 찾기(Known-Item Retrieval)" 방식은 정답이 정해져 있어 Open Domain 성능 평가에 부적합했습니다. 이를 개선하기 위해 **'카테고리 기반 가상 질문 생성'** 방식을 채택했습니다.

<details>
<summary>생성 프롬프트</summary>

```text
        [역할]
        당신은 관광지를 찾고싶은 여행객입니다.
        제시된 [카테고리]를 방문하고 싶어하는 사용자들이 던질 법한 질문을 {k}개 생성하세요. 반드시 {k}개를 생성해야합니다.
        단, 카테고리별로 세부적인 유형을 나누어서 질문을 생성하세요
        예를 들어 음식점의 경우 카페, 한식집, 양식집, 일식 전문점 등
        쇼핑의 경우 백화점, 전통시장등의 세부 유형을 나누어 질문을 생성하세요.
        
        [지침]
        1. 질문은 친구나 AI에게 말하는 듯한 자연스러운 구어체여야 합니다.
        2. 특정 장소 이름이나 특정 지역명(예: 종로, 시청)은 절대 포함하지 마세요.
        3. 각 질문은 서로 다른 상황(예: 혼자, 가족과, 데이트, 비즈니스 등)을 가정하여 다양하게 만드세요.
        4. 답변은 오직 질문 내용만 출력하며, 각 질문은 줄바꿈으로 구분하세요.      
        5. 절대로 부가적인 설명이나 번호등을 붙이지말고 정확히 5줄이 나오도록 출력하세요.  
        [카테고리]: {category}
```
</details>


*   **가설 설정**: 사용자는 특정 장소명(예: "스타벅스")보다는 추상적인 니즈(예: "분위기 좋은 카페")를 검색할 것이다.
*   **데이터 생성**: 8개 관광 카테고리(관광지, 음식점, 숙박 등)를 기준으로 LLM을 통해 자연어 질문을 생성했습니다. 이때, 각 카테고리 내부의 세부 카테고리로도 나누어 질문을 생성하도록 지시합니다.
(ex. 음식점 -> 카페, 일식당, 한식당, 중국집)

*   **다양성 확보**: 4가지 페르소나(가족 여행, 커플 데이트, 나홀로 여행, 비즈니스)를 부여하여 다양한 상황의 쿼리를 확보했습니다.
    *   *예시: "가족과 함께 가기 좋은...", "비즈니스 미팅 후 조용한..."*
*   **실험 규모**: 총 240개 쿼리 (API Rate Limit 고려 80개 × 3회 분할 수행)

<details>
<summary>예시</summary>

```text
- [관광지] Q: ['자연경관이 예쁜 관광지 중 가족과 함께 가기 좋은 곳은 어디가 있을까요?', '혼자 여행가서 역사 유적지를 탐방하기 좋은 곳을 추천해 주세요.', '커플이 함께 가볼 만한 로맨틱한 관광지가 있을까요?', '아이들과 함께 체험할 수 있는 교육적인 관광지를 찾고 있어요.', '비즈니스 미팅 후 가볍게 둘러보기 좋은 도시 속 관광지가 있을까요?', '야경이 아름다운 자연 관광지를 추천해 주실 수 있나요?', '전통 문화를 경험할 수 있는 관광지 중 외국인이 방문하기 편한 곳은요?', '도심에서 멀지 않은 산책하기 좋은 공원이 있을까요?', '특이한 암석이나 지형을 볼 수 있는 관광지를 알려주세요.', '계절별로 다른 매력을 느낄 수 있는 관광지 추천 부탁드립니다.']
- [문화시설] Q: ['문화시설에서 가족이나 친구와 함께 체험할 수 있는 전통 공예 프로그램이 있을까요?', '혼자 방문하기 좋은 조용한 미술관이나 박물관이 있을까요?', '데이트 코스로 적합한 야간 개장 문화시설이 있을까요?', '아이와 함께 가면 좋을 체험형 전시나 교육 프로그램이 있는 곳이 있을까요?', '비즈니스 미팅 후 가볍게 들르기 좋은 현대적인 갤러리나 복합 문화공간이 있을까요?', '역사 테마로 된 문화시설 중에서 사진 찍기 좋은 곳을 추천해 주세요.', '문화시설 중에서 반려동물과 함께 입장 가능한 곳이 있을까요?', '대중교통으로 접근하기 편한 문화시설 중 야외 공연장이 있을까요?', '문화시설 내에서 식사나 커피까지 함께 즐길 수 있는 복합 공간이 있을까요?', '문화시설 중 계절별로 특별 행사를 하는 곳을 알고 있나요?']
- [축제공연행사] Q: ['가족과 함께 즐길 만한 어린이 친화적 축제가 있을까요?', '커플과 분위기 있게 참여할 수 있는 야외 공연 행사가 있을까요?', '친구들과 가기 좋은 밤마다 열리는 축제나 행사가 있을까요?', '혼자 방문해도 부담 없이 즐길 수 있는 소규모 공연이 있을까요?', '비즈니스 미팅 후 참석 가능한 세련된 문화 행사가 있을까요?', '할머니와 함께 걷기 편한 전통 축제나 행사가 있을까요?', '반려동물과 동반 가능한 축제 또는 공연이 있을까요?', '비 오는 날 실내에서 즐길 수 있는 공연이나 행사가 있을까요?', '현지인들만 아는 숨은 축제 정보를 알 수 있을까요?', '계절별로 특색 있는 테마 공연이나 행사가 있을까요?']
- [여행코스] Q: ['혼자 여행하기 좋은 자연 경관이 있는 여행코스는 어디가 있을까요?', '가족들과 함께 즐길 수 있는 체험 프로그램이 많은 여행코스를 추천해 주세요.', '데이트 코스로 분위기 좋은 카페와 전망 명소가 있는 여행지를 찾고 있어요.', '비즈니스 미팅 후 가볍게 산책하기 좋은 도심 속 여행코스가 있을까요?', '아이들과 함께 교육적인 요소가 있는 박물관과 공원이 있는 여행지를 알려주세요.', '친구와 함께 액티비티를 즐길 수 있는 모험 위주의 여행코스는 어디인가요?', '전통 시장과 문화유산을 함께 경험할 수 있는 역사 테마 여행코스는 없을까요?', '휴가 기간에 휴식을 취하기 좋은 해변과 리조트가 있는 여행지를 추천해 주세요.', '혼자 조용히 책을 읽기 좋은 조용한 도서관과 카페가 있는 여행코스가 있을까요?', '현지인들만 아는 숨은 명소가 포함된 비주류 여행코스를 알고 싶어요.']
- [레포츠] Q: ['혼자 즐기기 좋은 실내 클라이밍 장소가 있을까요?', '가족과 함께 갈 수 있는 안전한 카트체험 장소는 어디인가요?', '데이트 코스로 추천할만한 패러글라이딩 스팟이 궁금해요.', '비즈니스 출장 중 짬내서 할 만한 짧은 서바이벌 게임이 있을까요?', '친구들과 가볼 만한 야간 스키장 추천 부탁드려요.', '아이들과 가기 좋은 수상 레포츠 체험장은 어디인지 알고 싶어요.', '커플이 함께 배우고 싶은 댄스 스튜디오가 있을까요?', '부모님과 도전해볼 수 있는 가벼운 트레킹 코스가 필요해요.', '혼행 중 새로운 경험을 위한 번지점프 장소 추천해주세요.', '반려동물과 함께 할 수 있는 애견 전용 수영장이 있나요?']
- [숙박] Q: ['혼자 여행 중에 편하게 쉴 수 있는 게스트하우스 어디 있을까요?', '가족과 함께 머물기 좋은 넓은 객실의 호텔 추천해 주세요.', '커플 데이트 분위기 좋은 로맨틱한 펜션은 어디에 있나요?', '비즈니스 출장을 위한 회의실 있는 숙소를 찾고 있어요.', '아이들과 함께 머물기 좋은 놀이시설이 있는 리조트 있을까요?', '동물 동반 가능한 숙소를 찾고 있는데 추천해 주세요.', '전통 한옥에서 묵어보고 싶은데 어디가 좋을까요?', '저렴한 가격에 깨끗한 모텔을 찾고 있어요.', '산 근처에서 자연 경관을 즐길 수 있는 산장형 숙소 있을까요?', '스파와 수영장이 있는 고급 리조트를 추천받고 싶어요.']
- [쇼핑] Q: ['가족들과 함께 가기 좋은 전통시장 어디 있을까요?', '혼자 쇼핑하기 편한 백화점 추천해주세요.', '데이트 코스로 좋은 명품 매장 밀집 지역은 어딜까요?', '해외 브랜드 직구 대행을 해주는 쇼핑센터 알고 싶어요.', '비즈니스 미팅 후 들르기 좋은 루프탑 쇼핑몰 있을까요?', '아이들과 함께 가기 좋은 장난감 전문점은 어디인가요?', '할인 혜택이 많은 디자이너 브랜드 아울렛은 어디에 있죠?', '야간 쇼핑 가능한 24시간 운영하는 매장 알고 싶어요.', '현지 특산품 구매하기 좋은 로컬 마켓은 어디가 있나요?', '친구 선물 사기 좋은 편집숍 밀집 지역은 어디예요?']
- [음식점] Q: ['혼자 먹기 좋은 분위기 있는 카페 어디 있을까요?', '가족과 함께 갈 만한 아이 친화적인 패밀리 레스토랑이 필요해요.', '데이트할 때 분위기 좋은 이탈리안 레스토랑이 있을까요?', '비즈니스 미팅하기 좋은 프라이빗한 다이닝 장소가 있을까요?', '친구들과 술 한잔 하며 수다 떨기 좋은 펍이나 바 추천해 주세요.', '신혼여행지 같은 로맨틱한 디너가 가능한 프렌치 레스토랑 있나요?', '혼밥하기 편한 한식당 중에서 가성비 좋은 곳 있을까요?', '아이들 데리고 가기 좋은 키즈 메뉴 있는 중식당이 필요해요.', '커플끼리 분위기 내기 좋은 티타임 카페 어디 있나요?', '혼자 여행 중 간단히 식사할 수 있는 현지 맛집 알려주세요.']
```
</details>

#### 1.4. 최종 성과: Hybrid & HyDE 검색 도입으로 추천 성능 20% 향상
위 실험 설계에 따라 생성된 240개의 쿼리(상위 10개 결과)에 대해 RAGAS 평가를 수행했습니다.

*   **평가 도구**: RAGAS Custom Evaluator (Category Alignment, Vibe Relevance)

평가 결과, **HyDE (Hypothetical Document Embeddings)** 및 **Hybrid (Sparse+Dense)** 방식이 **평균 0.79점대**를 기록하며 가장 우수한 성능을 보였습니다. 
단순 Dense 검색(0.66) 대비 **약 20%의 성능 향상**을 확인하였으며, 이를 통해 사용자의 모호한 의도를 파악하는 데에는 **하이브리드 또는 생성형 임베딩(HyDE)** 접근이 필수적임을 확인하여 이를 실제 관광지 추천 시스템에 적용하였습니다.

각 지표에 대한 수치는 아래와 같은 과정을 통해 산정됩니다.
- 1. 각 카테고리별로 생성된 쿼리(ex. 근처에 바다 뷰가 좋은 카페 추천해줘)를 기반으로 각 검색기 별로 상위 10개의 검색 결과를 받아옵니다.
  2. 각 검색 결과에 대해 사전 정의된 평가 기준에 따라 LLM as Judge를 수행합니다. 검색된 문서에 대해 평가 결과가 0 혹은 1로 반환됩니다.
  3. 모든 쿼리에 대해 각 검색기 별로 평가를 수행하여 쿼리 당 점수를 산출합니다. (문서 10개 중 7개가 1인 경우 0.7)
  4. 각 검색기 별로 지표당 점수에 평균을 냅니다. (Category Alignment, Vibe Relevance)
  5. Total Score는 Category Alignment와 Vibe Relevance에 각각0.7과 0.3의 가중치를 주어 합산합니다. (세부 카테고리가 검색 결과에서 일치하는 것이 더 중요하다 판단했습니다.)


#### [검색기 별 추천 성능 예시]
<img width="846" height="547" alt="image" src="https://github.com/user-attachments/assets/953baec9-88b5-4b4a-8b61-1029d21d7fa9" />
<img width="846" height="547" alt="image" src="https://github.com/user-attachments/assets/1e2e3962-9db0-4027-9051-833b172b3608" />
<img width="846" height="547" alt="image" src="https://github.com/user-attachments/assets/5e930c27-7a3f-451f-874c-c360de385057" />


| Retriever | Category Alignment (Avg) | Vibe Relevance (Avg) | **Total Score (Avg)** |
| :--- | :---: | :---: | :---: |
| **HyDE** | **0.8000** | 0.7741 | **0.7923** |
| **Hybrid** | 0.7741 | **0.8330** | **0.7918** |
| Hybrid-HyDE | 0.7694 | 0.7758 | 0.7714 |
| Ensemble | 0.7650 | 0.7766 | 0.7538 |
| Dense | 0.6422 | 0.7097 | 0.6625 |
| Sparse | 0.6503 | 0.6572 | 0.6566 |


<br>

### 2. 검색 파이프라인 최적화 시도
추출된 태그는 하나의 단어로 이루어져 있으며 해당 태그 자체가 관광지의 설명(Overview)를 함축하고 있습니다. 반면 문맥적인 정보는 가지고 있지 않기 때문에 기존 Overview와 동일한 형태로 임베딩 하는 것은 바람직 하지 않다 생각했습니다. <br>
때문에 빈도기반 유사도를 활용하여 BM25 검색기로 앙상블 하고자 하였습니다. 그러나 Qdrant에는 BM25 검색을 지원하는 인덱스가 존재하지 않았으며 이를 위해 별도의 DB를 두는 것은 관리 부담이 커진다는 단점으로 인해 다른 방법을 찾아야 했습니다. <br>
Qdrant에서 Sparse Vector에 대한 인덱스를 지원함을 확인하였고 **Sparse Embedding을 결합한 Hybrid 검색**을 도입했습니다. 이 과정에서 Sparse 검색의 품질을 높이기 위해 **'LLM 기반 태그(Tag) 추출'** 방식을 고안했습니다.
#### Sparse 검색의 특징
Sparse 검색은 Dense 검색과 대비되는 아래와 같은 특징을 가집니다.
* 고차원성
    * 수천에서 수백만 차원의 고차원을 사용
* 지역성
    * 각 단어를 독립적으로 표현
    * '카페'와 '음식점'을 완전히 다른 차원으로 처리

위와 같은 특징으로 인해 dense 검색의 약점인 세부 카테고리 내에서 발생하는 유사성 차이를 효과적으로 포착할 수 있을 것이라 판단했습니다 .

#### 2.1. Hybrid 검색을 위한 태그(Tag) 추출 전략
*   **가설 및 접근**: "관광지 설명(Overview)의 전체 텍스트보다는, 그 의미를 함축하는 핵심 키워드(Tag)가 검색 매칭에 더 효과적일 것이다."
*   **구현 프로세스**:
    1.  **Tag Extraction**: LLM을 통해 각 관광지 Overview에서 '분위기', '목적', '특징'을 나타내는 태그를 추출 (예: `#조용한`, `#야경맛집`, `#데이트코스`, '#파인다이닝').
    2.  **Sparse Indexing**: 추출된 태그들을 하나의 텍스트로 결합하여 **Splade(Sparse Embedding)** 인덱스를 구축.
    3.  **Hybrid Search**: 사용자 쿼리에 대해 Dense(의미) 점수와 Sparse(태그 키워드) 점수를 가중합산(Weighted Sum)하여 최종 순위 결정.

#### 2.2. Sparse 모델 선정 및 서빙 전략 (GPU Indexing / CPU Serving)

*   **모델 성능 비교**:
    *   **`naver/splade-v3`**: 한국어로 전혀 학습이 되어있지 않아 검색에 사용할 수 없었습니다.
    *   **`yjoonjang/splade-ko-v1`**: **Hit Rate@5**가 가장 우수했으나, CPU 환경에서 인덱싱(저장) 속도가 매우 느린 단점이 있습니다.
    *   **`Qdrant/bm25`** : FastEmbed를 지원하는 모델로 인덱싱 및 실시간 검색에서 매우 빠르다는 특징이 있지만, 한국어로 학습되어 있지 않아 검색 성능이 매우 처참했습니다.
    <img width="1081" height="750" alt="image" src="https://github.com/user-attachments/assets/289233ce-c0b2-44a3-b7ce-c5aaacf5328f" />
    <img width="672" height="123" alt="image" src="https://github.com/user-attachments/assets/3050b89a-2936-4773-b907-f002578e345b" />


*   **최적화 결정**:
    *   성능 타협 없이 **`Splade-ko-v1`**을 채택.
    *   **파이프라인 이원화**: 리소스가 많이 드는 **인덱싱(저장)은 GPU 환경**에서 배치로 미리 수행하고, 실시간 **검색(Serving)은 CPU 환경**에서 수행(쿼리당 약 0.3초)하는 구조로 배포 효율성을 확보했습니다.

<br>

### 3. Vector Store 호환성 문제 트러블슈팅

#### 문제 상황
LangChain의 `QdrantVectorStore`를 사용하는 과정에서, 기존 구축된 Qdrant Collection의 Payload(데이터)가 LangChain `Document` 객체의 `metadata`로 정상적으로 매핑되지 않는 호환성 문제가 발생했습니다.
<img width="986" height="213" alt="image" src="https://github.com/user-attachments/assets/06e75459-62a4-4d6c-aa0e-21c19af840b0" />

#### 해결 과정
1.  **원인 분석**: LangChain-Qdrant에서 QdrantVectorStore 내부 로직이 `metadata_payload_key`를 지정해도 중첩된 구조나 특정 필드 매핑을 유연하게 처리하지 못함을 확인했습니다. 반면, QdrantClient를 통해 직접 요청을 보내어 응답을 받을 때는 정상적으로 데이터들어오는 것을 확인했습니다.
이 문제를 해결 하기 위해 크게 2가지 대안을 생각했습니다.

<img width="920" height="777" alt="image" src="https://github.com/user-attachments/assets/ca172e2b-7268-4fc7-b581-a927660a6f72" />


3.  **대안 비교**:
    *   *안 1*: 데이터를 `LangChain` 포맷에 맞게 전수 **Re-indexing** 수행 (약 2시간 소요 예상, 운영 리스크 큼).
    *   *안 2*: 라이브러리를 상속받아 **Custom Wrapper** 구현.
4.  **최종 결정**: 1번의 경우 데이터수가 5만건에도 약 2시간 정도의 시간이 걸리는 편이지만, 만약 훨씬 더 데이터가 많거나, 실시간으로 데이터 추가된다면 좋은 선택지가 아니라 판단했습니다. 따라서 `CustomQdrantVectorStore` 클래스를 구현하여 `_document_from_point` 메서드를 오버라이딩했습니다. 이를 통해 기존 데이터를 건드리지 않고도 Payload를 Document 객체로 변환하는 데 성공했습니다.

```python
class CustomQdrantVectorStore(QdrantVectorStore):
    @classmethod
    def _document_from_point(
        cls,
        scored_point: Any,
        collection_name: str,
        content_payload_key: str,
        metadata_payload_key: str,
    ) -> Document:
        # scored_point.payload 전체를 metadata로 사용
        payload: Dict[str, Any] = scored_point.payload or {}

        # page_content: title 또는 content_payload_key 지정값
        title_key = content_payload_key or "title"
        page_content = payload.get(title_key, "")

        # metadata: payload 전체 복사
        metadata: Dict[str, Any] = dict(payload)

        # QdrantVectorStore 기본 메타 필드 유지
        metadata["_id"] = scored_point.id
        metadata["_collection_name"] = collection_name

        return Document(
            page_content=page_content,
            metadata=metadata,
        )
```
<img width="977" height="758" alt="image" src="https://github.com/user-attachments/assets/656d85b9-d0e5-4804-9bb0-4292ddedcae1" />

<br>

### 4. LangGraph 기반 여행 계획 자동 생성 파이프라인

단순한 선형적 LLM 호출(Chain)로는 복잡한 사용자 요구사항과 예외 상황을 처리하는 데 한계가 있었습니다. 이를 해결하기 위해 순환형 상태 관리 프레임워크인 **LangGraph**를 도입하여, 스스로 검색 품질을 평가하고 계획을 수정하는 Self-RAG 파이프라인을 구축했습니다.

#### 4.1. 파이프라인 구조 (Workflow)
여행 계획 생성 프로세스를 다음과 같은 Node와 Edge로 정의하여 유연성을 확보했습니다.
<img width="330" height="853" alt="image" src="https://github.com/user-attachments/assets/4884aeae-8632-4412-ac6c-e902d99638d1" />

*   **State Management**: `PlanState`를 통해 검색 결과, 재시도 횟수, 피드백 등을 전역적으로 관리.
*   **주요 프로세스**:
    1.  **Attraction Load**: 사용자 선택 관광지 정보 로드.
    2.  **Query Rewrite**: 사용자 요구사항을 검색에 최적화된 쿼리로 재작성.
    3.  **Similar Search**: 하이브리드 검색 수행.
    4.  **Search Evaluator (Self-Correction)**:
        *   검색 결과가 사용자 의도에 부합하는지 LLM이 자체 평가.
        *   부적합 판정 시 `Query Rewrite` 단계로 회귀하여 **최대 3회 재검색** 수행 (Loop).
    5.  **Trip Type Check**: 당일치기/숙박 여부를 판단하여 `Accommodation Search` 단계 실행 여부 결정 (Conditional Edge).
    6.  **Plan Generate**: 수집된 정보를 바탕으로 최종 여행 계획 생성.
    7.  **Plan Review**: 생성된 계획의 논리적 오류(동선, 시간 등) 검증. 오류 발견 시 재생성 (Loop).

#### 4.2. 도입 효과
*   **환각(Hallucination) 최소화**: 검색 품질 평가 루프를 통해 엉뚱한 장소가 포함될 확률을 사전에 차단.
*   **복합 추론 가능**: "당일치기면 숙소 검색 생략", "검색 실패 시 쿼리 수정" 등 조건부 로직을 명시적으로 구현하여 시스템 안정성 확보.

<br>

## 프로젝트 관리 (Appendix)

### WBS - 일정 관리
<img width="547" height="308" alt="image" src="https://github.com/user-attachments/assets/2e1e6a2f-5788-4f3c-92f8-f06402f1690a" />
