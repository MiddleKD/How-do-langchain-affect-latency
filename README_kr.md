# How Do LangChain Affect Latency?

Langchain과 Celery가 성능에 주는 영향 비교 테스트

## 공통 설정

* **LLM Backend**: Ollama (llama3.1 / RTX 4090)
* **API 서버**: FastAPI
* **Task Queue (해당 시)**: Celery + Redis
* **Ramp-up 조건**:

  * **300명 테스트**: 3분간 초당 5명 증가
  * **1000명 테스트**: 3분간 초당 10명 증가

---

## 테스트 결과 (300명 / 1000명 동접)

| Case                 | 동접   | Type        | Name                        | Requests | Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Failures/s |
| -------------------- | ---- | ----------- | --------------------------- | -------- | ----- | ----------- | ----------- | ----------- | ------------ | -------- | -------- | ---------------- | ----------- | ---------- |
| Pure Python          | 300  | POST        | /generate                   | 4608     | 0     | 9600        | 11000       | 11000       | 8021.21      | 219      | 11597    | 145.36           | 27.3        | 0          |
| Pure Python          | 1000 | POST        | /generate                   | 4603     | 0     | 24000       | 38000       | 38000       | 22912.62     | 331      | 39332    | 147.26           | 25.8        | 0          |
| Langchain            | 300  | POST        | /generate                   | 4633     | 0     | 9500        | 11000       | 11000       | 7969.42      | 175      | 11557    | 144.6            | 25.8        | 0          |
| Langchain            | 1000 | POST        | /generate                   | 3683     | 0     | 22000       | 58000       | 59000       | 27062.88     | 213      | 59776    | 145.36           | 12.3        | 0          |
| Pure Python + Celery | 300  | POST+GET(s) | /generate + /result polling | 4589     | 0     | 9600        | 11000       | 11000       | 8041.02      | 308      | 11947    | 0                | 25.0        | 0          |
| Pure Python + Celery | 1000 | POST+GET(s) | /generate + /result polling | 4627     | 0     | 25000       | 37000       | 37000       | 22920.69     | 310      | 38575    | 0                | 26.2        | 0          |
| Langchain + Celery   | 300  | POST+GET(s) | /generate + /result polling | 4513     | 0     | 9700        | 11000       | 11000       | 8194.09      | 207      | 11777    | 0                | 26.3        | 0          |
| Langchain + Celery   | 1000 | POST+GET(s) | /generate + /result polling | 4568     | 0     | 24000       | 38000       | 39000       | 23275.62     | 308      | 39615    | 0                | 27.6        | 0          |

---

# ✅ 성능 비교 분석 요약

## 📊 1. Pure Python vs LangChain

| 동접   | 지표      | Pure Python | LangChain | 차이                            |
| ---- | ------- | ----------- | --------- | ----------------------------- |
| 300  | 평균 응답시간 | 8021 ms     | 7969 ms   | ≈ 동일                          |
| 1000 | 평균 응답시간 | 22912 ms    | 27062 ms  | **LangChain이 느림 (+18%)** |

✅ **해석**

300명 시점에서는 LangChain 도입이 큰 차이 없음.
1000명 시점에서는 LangChain 사용 시 오버헤드 발생 (약 18% 느림).
**LangChain 내부의 불필요한 대기 시간 존재 가능성**

---

## 📊 2. Celery 도입 효과 (Pure Python 기준)

| 동접   | 지표      | Non-Celery | Celery   | 차이   |
| ---- | ------- | ---------- | -------- | ---- |
| 300  | 평균 응답시간 | 8021 ms    | 8041 ms  | ≈ 동일 |
| 1000 | 평균 응답시간 | 22912 ms   | 22920 ms | ≈ 동일 |

✅ **해석**

Celery 적용 여부가 대기열 지연을 별로 줄이지 못함.
싱글 노드 / 단일 워커인 경우 이점 없음.
(여러 Worker 분산 처리시 개선될 여지 있음)

---

## 📊 3. LangChain + Celery 조합 효과

| 동접   | 지표      | LangChain Only | LangChain + Celery | 차이                         |
| ---- | ------- | -------------- | ------------------ | -------------------------- |
| 300  | 평균 응답시간 | 7969 ms        | 8194 ms            | 약간 느림 (+2\~3%)             |
| 1000 | 평균 응답시간 | 27062 ms       | 23275 ms           | **Celery 버전이 더 빠름 (-14%)** |

✅ **해석**

LangChain + Celery 조합이 1000명 시점에서는 오히려 성능 개선 효과 보임. 300명은 오차 범위 내라고 생각.
**LangChain 내부의 불필요한 대기 시간 존재 가능성**

---

## ✅ 최종 종합 요약

| 동접   | 최저 평균 응답시간 케이스                 |
| ---- | ------------------------------ |
| 300  | Pure Python / LangChain 거의 동일  |
| 1000 | **LangChain + Celery** 가 가장 빠름 |

✅ **결론**

* **소규모 트래픽:** 단순 Python, LangChain, Celery 여부 관계 없음
* **대규모 트래픽:** Langchain 사용 자제. 비동기큐 + 단순 파이썬 구현이 유리 => 지표상 Langchain + celery가 가장 좋지만, [📊 1. Pure Python vs LangChain](#-1-pure-python-vs-langchain) 를 무시할 수 없음
---
