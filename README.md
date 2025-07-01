# How Do LangChain Affect Latency?

A load test comparing how much LangChain and Celery impact API latency.

## Common Test Setup

* **LLM Backend**: Ollama (llama3.1 / RTX 4090)
* **API Server**: FastAPI
* **Task Queue (when used)**: Celery + Redis
* **Ramp-up Profile**:

  * **300 users test**: 3 minutes ramp-up, +5 users per second
  * **1000 users test**: 3 minutes ramp-up, +10 users per second

---

## Test Results (300 / 1000 concurrent users)

| Case                 | Concurrency | Type        | Name                        | Requests | Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Failures/s |
| -------------------- | ----------- | ----------- | --------------------------- | -------- | ----- | ----------- | ----------- | ----------- | ------------ | -------- | -------- | ---------------- | ----------- | ---------- |
| Pure Python          | 300         | POST        | /generate                   | 4608     | 0     | 9600        | 11000       | 11000       | 8021.21      | 219      | 11597    | 145.36           | 27.3        | 0          |
| Pure Python          | 1000        | POST        | /generate                   | 4603     | 0     | 24000       | 38000       | 38000       | 22912.62     | 331      | 39332    | 147.26           | 25.8        | 0          |
| LangChain            | 300         | POST        | /generate                   | 4633     | 0     | 9500        | 11000       | 11000       | 7969.42      | 175      | 11557    | 144.6            | 25.8        | 0          |
| LangChain            | 1000        | POST        | /generate                   | 3683     | 0     | 22000       | 58000       | 59000       | 27062.88     | 213      | 59776    | 145.36           | 12.3        | 0          |
| Pure Python + Celery | 300         | POST+GET(s) | /generate + /result polling | 4589     | 0     | 9600        | 11000       | 11000       | 8041.02      | 308      | 11947    | 0                | 25.0        | 0          |
| Pure Python + Celery | 1000        | POST+GET(s) | /generate + /result polling | 4627     | 0     | 25000       | 37000       | 37000       | 22920.69     | 310      | 38575    | 0                | 26.2        | 0          |
| LangChain + Celery   | 300         | POST+GET(s) | /generate + /result polling | 4513     | 0     | 9700        | 11000       | 11000       | 8194.09      | 207      | 11777    | 0                | 26.3        | 0          |
| LangChain + Celery   | 1000        | POST+GET(s) | /generate + /result polling | 4568     | 0     | 24000       | 38000       | 39000       | 23275.62     | 308      | 39615    | 0                | 27.6        | 0          |

---

# ✅ Summary: Performance Comparison & Analysis

## 📊 1. Pure Python vs LangChain

| Concurrency | Metric      | Pure Python | LangChain | Difference                     |
| ----------- | ----------- | ----------- | --------- | ------------------------------ |
| 300         | Avg Latency | 8021 ms     | 7969 ms   | ≈ No significant difference    |
| 1000        | Avg Latency | 22912 ms    | 27062 ms  | **LangChain is slower (+18%)** |

✅ **Interpretation**

At 300 users: LangChain shows no real impact on latency.
At 1000 users: LangChain adds overhead, causing \~18% higher latency.
**Potential Cause:** Possible internal queuing/wait time inside LangChain.

---

## 📊 2. Celery Queueing Impact (Pure Python baseline)

| Concurrency | Metric      | Non-Celery | Celery   | Difference      |
| ----------- | ----------- | ---------- | -------- | --------------- |
| 300         | Avg Latency | 8021 ms    | 8041 ms  | ≈ No difference |
| 1000        | Avg Latency | 22912 ms   | 22920 ms | ≈ No difference |

✅ **Interpretation**

Celery made little to no latency difference at this scale (single worker).
**Reason:** Benefits of Celery appear mostly in multi-worker distributed setups, not in single-node.

---

## 📊 3. LangChain + Celery Combo Effect

| Concurrency | Metric      | LangChain Only | LangChain + Celery | Difference                          |
| ----------- | ----------- | -------------- | ------------------ | ----------------------------------- |
| 300         | Avg Latency | 7969 ms        | 8194 ms            | Slightly slower (+2\~3%)            |
| 1000        | Avg Latency | 27062 ms       | 23275 ms           | **Celery version is faster (-14%)** |

✅ **Interpretation**

At 1000 users: The **LangChain + Celery** setup was surprisingly faster.
At 300 users: Difference is within margin of error.
**Possible Reason:** Celery’s queuing and scheduling effects mitigate LangChain's internal delays under high load.

---

## ✅ Final Overall Summary

| Concurrency | Best Avg Latency Case              |
| ----------- | ---------------------------------- |
| 300         | Pure Python / LangChain (similar)  |
| 1000        | **LangChain + Celery** was fastest |

✅ **Takeaways**

* **For small traffic:** Celery or LangChain doesn't matter much.
* **For high traffic:**
  LangChain alone adds overhead.
  **Async queue (Celery) + lightweight Python implementation is preferred.**
  However: While **LangChain + Celery was the fastest**,
  you **shouldn't ignore the LangChain overhead shown in [📊 1. Pure Python vs LangChain](#-1-pure-python-vs-langchain).**

---
