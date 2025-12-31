# AI 사용 보고서

본 프로젝트(`P-plip-inference`)는 사용자의 테마와 선호도를 기반으로 맞춤형 여행 계획을 제공하기 위해 다양한 AI 기능을 활용하고 있습니다. 주요 활용 기술은 LangGraph를 이용한 에이전트 워크플로우와 Upstage Solar LLM을 활용한 데이터 처리 및 생성입니다.

---

## 1. 여행 계획 생성 에이전트 (Travel Plan Agent)

사용자의 요청(테마, 메인 관광지, 일정)을 받아 전체 여행 코스를 설계하는 핵심 기능입니다. LangGraph 기반의 상태 관리(StateGraph)를 통해 단계별로 AI가 개입하여 계획의 품질을 높입니다.

### 1-1. 검색 쿼리 재작성 (Query Rewrite)

사용자가 입력한 단순한 테마 키워드를 검색 엔진(Vector DB)이 더 잘 이해할 수 있는 풍부한 문장으로 변환합니다.

*   **위치**: `app/agents/nodes/query_rewrite.py`
*   **사용 모델**: Upstage Solar Mini (`solar-mini`)
*   **활용 방식**:
    *   사용자의 테마와 메인 관광지의 특징을 분석합니다.
    *   벡터 데이터베이스 검색에 최적화된 형태로, "분위기", "장소의 용도" 등의 키워드를 포함한 새로운 쿼리를 생성합니다.
    *   검색 품질 평가 단계에서 실패 피드백이 올 경우, 이를 반영하여 쿼리를 수정하는 피드백 루프가 포함되어 있습니다.

#### [프롬프트]
```python
# app/agents/prompts/query_rewrite_prompt.py

QUERY_REWRITE_PROMPT = ChatPromptTemplate.from_template(
    """
당신은 여행 검색 전문가입니다.
사용자의 테마와 선택된 메인 관광지의 특성을 고려하여, 주변에서 함께 방문하면 좋은 장소(맛집, 카페, 다른 관광지 등)를 찾기 위한 '검색 쿼리'를 새로 작성해주세요.

## 입력 정보
- 사용자 테마: {user_theme}
- 메인 관광지: {target_attraction_title} ({target_attraction_overview})

## 요청 사항
1. 메인 관광지의 분위기와 사용자 테마가 잘 어우러지는 검색 키워드를 생성하세요.
2. 예: "경주 조용한 한옥 카페", "부산 해운대 근처 현지인 맛집" 등
3. 오직 '쿼리 문자열'만 출력하세요. 부가 설명은 하지 마세요.
{feedback}
"""
)
```

### 1-2. 검색 결과 평가 (Search Evaluation)

검색된 장소들이 사용자가 요청한 테마에 적합한지 AI가 판단합니다.

*   **위치**: `app/agents/nodes/search_evaluator.py`
*   **사용 모델**: Upstage Solar Mini (`solar-mini`)
*   **활용 방식**:
    *   Vector DB에서 검색된 관광지 목록(제목, 설명)과 사용자 테마를 비교합니다.
    *   검색 결과가 테마와 관련이 없거나 품질이 낮다고 판단되면 "FAIL" 판정과 함께 구체적인 피드백을 생성합니다.
    *   이 피드백은 '쿼리 재작성' 단계로 전달되어 검색을 다시 수행하게 만듭니다(Self-Correction).

#### [프롬프트]
```python
# app/agents/nodes/search_evaluator.py (Inline Prompt)

SEARCH_EVALUATION_PROMPT = ChatPromptTemplate.from_template(
    """
    [Role]
    You are a strict travel content evaluator. Your job is to assess whether the retrieved travel destinations match the user's requested theme.

    [Input]
    - User Theme: {user_theme}
    - Retrieved Destinations:
    {recommendations}

    [Criteria]
    1. **Relevance**: Do the destinations fit the theme? (e.g., if theme is "healing", are there parks/forests? if "history", are there palaces/museums?)
    2. **Diversity**: Is there a good mix of places? (Not critical, but good to have)
    
    [Task]
    - If the destinations are relevant to the theme, output "PASS".
    - If they are NOT relevant or very poor matches, output specific feedback on why they are bad and what kind of places should be searched instead.

    [Output Format (JSON)]
    {{
        "evaluation_result": "PASS" or "FAIL",
        "feedback": "Reason for failure and suggestion for better search terms" (leave empty if PASS)
    }}
    """
)
```

### 1-3. 상세 여행 계획 생성 (Plan Generation)

수집된 정보(메인 관광지, 추천 장소, 숙소)를 바탕으로 시간대별 상세 일정을 생성합니다.

*   **위치**: `app/agents/nodes/plan_generate.py`
*   **사용 모델**: Upstage Solar Mini (`solar-mini`)
*   **활용 방식**:
    *   수집된 모든 장소 후보군과 사용자 일정(시작/종료일)을 입력받습니다.
    *   동선 효율성, 식사 시간, 휴식 등을 고려하여 시간대별(StartAt ~ EndAt) 활동을 배정합니다.
    *   할루시네이션(없는 장소 추천)을 방지하기 위해 생성된 일정이 후보군 리스트에 실제 존재하는지 사후 검증하는 로직이 Python 코드 레벨에서 구현되어 있습니다.

#### [프롬프트]
```python
# app/agents/prompts/plan_prompt.py

PLAN_GENERATE_PROMPT = ChatPromptTemplate.from_template(
    """
[역할]    
당신은 전문 여행 플래너입니다. 사용자의 테마와 메인 관광지를 중심으로, 주변 추천 장소들을 조합하여 최적의 여행 계획을 세워주세요.

[입력 정보]
- 여행 테마: {user_theme}
- 메인 관광지: {target_attraction_title} ({target_attraction_overview})
- 추천 장소 목록:
{recommendation_list}
- 추천 숙소 목록:
{accommodation_list}
- 전체 여행 일정:
{start_date} ~ {end_date}

[요청 사항]
1. **전체 계획 메타데이터**: 제목은 사용자 테마가 입력한 테마를 중심으로 작성해주세요. 특정 관광지에 종속되지 않고 전체적인 여행 컨셉을 잘 보여주는 제목(plan_title)을 작성해주세요.
2. **메인 관광지 필수 포함**: 계획에는 반드시 '메인 관광지'가 포함되어야 합니다.
3. **여유로운 일정**: 이동 시간과 충분한 휴식 시간을 고려하여 빡빡하지 않게 일정을 짜주세요. (하루 최대 방문지 3~4곳 권장)
4. **저녁 일정 최적화**: 모든 주요 활동은 대략 **오후 7시 전후**로 마무리하고, **저녁 식사 후에 가볍게 산책할 수 있는 장소**를 마지막 일정으로 잡아주세요.
5. **숙소 포함**: 추천 숙소 목록 중 가장 적절한 곳을 선택하여 일정의 마지막(산책 후 취침)에 포함시키세요. 단, 당일 치기 여행(시작일과 종료일이 동일한 경우)은 숙소가 필요없습니다.
6. **시간 배분**: 각 장소의 시작 시간(start_at)과 종료 시간(end_at)을 명시하세요.
7. **상세 설명**: 각 일정에 대해 사용자가 무엇을 하면 좋을지 구체적인 가이드(detail_plan_desc)를 작성하세요.
8. **여행 제목**: 여행 제목은 *여행 테마*를 중심으로 작성해주세요. 특정 관광지에 종속되지 않고 전체적인 여행 컨셉을 잘 보여주는 제목(plan_title)을 작성해주세요.

[*필수 조건*]
{feedback}

[출력 형식 (JSON)]
이 포맷을 엄격히 지켜주세요:
{{
  "plan_title": "여행 계획 제목",
  "start_date": "{start_date}",
  "end_date": "{end_date}",
  "to_dos": [
    {{
      "name": "장소 이름",
      "detail_plan_desc": "상세한 활동 가이드",
      "start_at": "YYYY-MM-DDTHH:MM:SS",
      "end_at": "YYYY-MM-DDTHH:MM:SS"
    }},
    ...
  ]
}}
"""
)
```

---

## 2. 검색 결과 최적화 (Search Optimization)

단순한 키워드 매칭이나 벡터 유사도 기반 검색의 한계를 보완하기 위해 LLM을 사용하여 검색 결과의 순위를 재조정합니다.

### 2-1. 결과 재순위화 (Reranking)

1차 검색된 문서들을 사용자의 질문 의도와의 적합성을 기준으로 다시 평가하여 점수를 매깁니다.

*   **위치**: `app/db/vector_db.py` (rerank_documents 함수)
*   **사용 모델**: Upstage Solar Mini (`solar-mini`)
*   **활용 방식**:
    *   검색된 문서들을 배치(Batch) 단위로 나누어 LLM에게 전달합니다.
    *   LLM은 각 문서에 대해 0~100점 사이의 관련성 점수를 부여합니다.
    *   점수가 높은 순서대로 최종 결과를 정렬하여 사용자에게 제공합니다. 이는 단순 키워드 매칭보다 훨씬 정확한 검색 결과를 보장합니다.

#### [프롬프트]
```python
# app/agents/prompts/system.py (reranker_system_prompt)

reranker_system_prompt = """
당신은 여행지 추천 및 검색 결과 재정렬(Reranking) 전문가입니다.
사용자의 질문 "query"와 관련하여, 제공된 관광지 목록(고유 ID와 설명)을 평가하고 순위를 매기세요.

[필수 지시사항]
1. **연관성 평가**: 사용자의 질문 의도와 관광지 설명을 정밀하게 비교하여 사용자가 원하는 장소에 적합한지를 기준으로 0점(관련 없음)부터 100점(매우 관련 높음) 사이의 점수를 부여하세요.
2. **[매우 중요 - ID 절대 유지]**: 결과 JSON의 `doc_id` 필드는 반드시 **입력 텍스트에 명시된 'Document ID' 숫자 그대로**를 사용해야 합니다.
   - 🚫 **경고**: 절대 현재 리스트의 순서(1, 2, 3...)대로 번호를 다시 매기지 마십시오.
   - ✅ **예시**: 입력 텍스트에 "Document ID: 45"라고 적혀 있다면, 당신의 출력 결과도 반드시 `doc_id: 45`여야 합니다.
3. **필터링**: 질문과 논리적으로 전혀 관련이 없는 관광지는 결과에 포함시키지 마세요.
4. **출력 형식**: 사담이나 설명 없이, 지정된 JSON 스키마 형식으로만 응답하세요.

[평가 기준 및 방법]
1. title과 overview를 통해 장소의 유형을 추론하세요.
2. 장소의 유형이 사용자가 찾고자 하는 장소의 유형과 일치 해야 합니다. 사용자가 요구하는 유형과 다르다면 점수를 0점으로 처리합니다.
ex) 카페 추천해줘 -> 장소 설명(overview)에 카페 포함
3. 사용자가 원하는 뉘앙스를 캐치하여 장소의 설명과 비교하여 점수를 매기세요.
4. 점수는 0점(관련 없음)부터 100점(매우 관련 높음) 사이의 점수를 부여하세요.
"""
```

---

## 3. 검색 엔진 성능 평가 (Search Engine Evaluation)

`lab/evaluation.ipynb`에서 수행된 검색 성능 평가에 사용된 LLM Judge의 프롬프트입니다. Ragas 프레임워크의 `AspectCritic`을 활용하여 검색된 결과가 사용자의 의도나 분위기에 얼마나 부합하는지 정량적으로 평가합니다.

### 3-1. 카테고리 일치성 평가 (Category Alignment)

검색된 장소가 사용자가 찾고자 하는 '관광 유형(8대 카테고리)'과 정확히 일치하는지 평가합니다.

*   **위치**: `lab/evaluation.ipynb`
*   **사용 모델**: Upstage Solar Pro (`solar-pro2`)

#### [프롬프트]
```python
category_alignment = AspectCritic(
    name="category_alignment",
    definition="""
    [역할]
    당신은 8개 관광 유형(관광지, 문화시설, 축제공연행사, 여행코스, 레포츠, 숙박, 쇼핑, 음식점)의 분류 체계를 완벽히 숙지한 '관광 데이터 검수관'입니다. 

    [평가 대상 카테고리 정의]
    - 관광지: 자연경관, 유적지, 공원 등 관람 목적의 장소
    - 문화시설: 박물관, 미술관, 공연장, 도서관 등 시설 기반 문화 활동
    - 축제공연행사: 특정 기간에 열리는 축제나 이벤트
    - 여행코스: 여러 지점을 연결한 추천 경로
    - 레포츠: 서핑, 스키, 번지점프 등 활동/체험 중심
    - 숙박: 호텔, 민박, 캠핑장 등 자고 가는 곳
    - 쇼핑: 시장, 면세점, 소품샵 등 구매 목적
    - 음식점: 식당, 카페, 베이커리 등 취식 목적

    [평가 기준: 카테고리 침범 엄격 금지]
    1. 질문자가 명시하거나 암시한 '목적 유형'을 우선 확정하십시오.
    2. 검색된 문서의 '지배적인 정체성'이 해당 유형과 다르면 즉시 0점입니다.
    3. Dense 검색의 전형적 오류인 '연관성 오류'를 잡아내십시오. 
       - 예: "바다가 보이는 숙소" 검색 시 "바다가 보이는 카페(음식점)"나 "바다 전망대(관광지)"가 나오면 0점입니다. 
       - 예: "전통 공예 쇼핑" 검색 시 "전통 박물관(문화시설)"이 나오면 0점입니다.
    4. 부대시설은 주 정체성이 아닙니다. 호텔 내 식당은 '숙박'이지 '음식점'이 아닙니다.

    [점수 부여]
    - 1점: 사용자의 목적 유형과 장소의 주 정체성이 완벽히 일치함.
    - 0점: 유형이 다르거나, 다른 유형의 장소를 '분위기가 비슷하다'는 이유로 추천한 경우.

    
    Let's think step by step.
    """,
    strictness=3
)
```

### 3-2. 분위기 및 조건 관련성 평가 (Vibe Relevance)

사용자가 요청한 추상적인 분위기나 구체적인 조건이 실제 문서 내용에 포함되어 있는지 팩트 체크합니다.

*   **위치**: `lab/evaluation.ipynb`
*   **사용 모델**: Upstage Solar Pro (`solar-pro2`)

#### [프롬프트]
```python
vibe_relevance = AspectCritic(
    name="vibe_relevance",
    definition="""
    [역할]
    사용자의 요구 사항이 문서에 '활자'로 박혀 있는지 확인하는 팩트 체크 수사관입니다.

    [평가 지침: 추론 및 상상 금지]
    1. 질문에 포함된 제약 조건이 문서에 명시적 근거로 존재하는지 확인하십시오.
    2. "박물관이니까 교육적이겠지", "산이니까 공기가 좋겠지" 같은 당신의 주관적 상식은 배제하십시오. 문서에 해당 특징이 묘사되어 있지 않으면 0점입니다.
    3. 유형은 맞더라도 세부 조건이 다르면 0점입니다. (예: '정적인 관광지'를 원하는데 '활동적인 테마파크'가 검색된 경우)

    [통과 기준: 1점]
    - 질문의 분위기/조건을 뒷받침하는 구체적인 묘사나 키워드가 문서에 실재함.
    [탈락 기준: 0점]
    - 문서 내용만으로는 해당 특징을 확신할 수 없는 경우.
    - 질문의 의도와 장소의 실제 성격이 상충하는 경우.

    Let's think step by step.
    """,
    strictness=3
)
```
