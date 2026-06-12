# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key hardcode included inside the code - leaked API key when pushing to GitHub repo
2. No config management
3. Print instead of proper logging
4. No health check endpoints - crashed agent cannot be restarted properly
5. Static port (8000), only works in localhost, debug reload in production
6. No error handling - crash occurs when ask() throw exception
7. No tests or CI/CD - invinsible bugs occur unless deployment is done
8. No documentation or API schema

### Exercise 1.3: Comparison table
| Feature | Basic (Anti-pattern) | Advanced (Production-ready) | Tại sao quan trọng? |
| :--- | :--- | :--- | :--- |
| **Cấu hình (Config)** | Hardcode trong code | Environment Variables | Bảo mật secret (API Key) và linh hoạt giữa các môi trường (Dev/Prod). |
| **Health Check** | Không có | Có `/health` & `/ready` | Giúp hệ thống tự động phát hiện nếu Agent treo để khởi động lại. |
| **Logging** | `print()` | Structured JSON Logging | Dễ dàng lọc và phân tích lỗi trên các hệ thống tập trung như CloudWatch/Loki. |
| **Shutdown** | Đắt ngang xương | Graceful Shutdown | Đảm bảo các request đang xử lý được hoàn tất trước khi tắt server. |
| **Network Binding** | `localhost` | `0.0.0.0` | Cho phép truy cập Agent từ bên ngoài container/cloud. |
| **Port Management** | Cố định (8000) | Đọc từ biến `PORT` | Cần thiết để chạy trên các nền tảng như Railway, Render, Heroku. |
| **Error Handling** | Sơ sài | Middleware & Exception Handling | Tránh việc server sập hoàn toàn khi gặp một lỗi nhỏ từ LLM. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: Python:3.11
2. Working directory: /app
3. Mục đích của việc tách riêng COPY requirements.txt và RUN pip install trước khi COPY toàn bộ source code? Tận dụng Docker layer cache. Vì file requirements.txt ít khi thay đổi hơn source code, việc tách riêng giúp Docker không phải cài đặt lại toàn bộ dependencies mỗi khi bạn sửa code trong app.py, từ đó tăng tốc độ build container đáng kể.
4. So sánh CMD và ENTRYPOINT
| Đặc điểm | `CMD` | `ENTRYPOINT` |
| :--- | :--- | :--- |
| **Mục đích** | Định nghĩa lệnh hoặc tham số mặc định. | Định nghĩa lệnh chính, cố định của container. |
| **Khi chạy `docker run <image> <args>`** | Toàn bộ `CMD` sẽ bị `<args>` **thay thế hoàn toàn**. | `<args>` sẽ được **nối thêm** vào sau `ENTRYPOINT`. |
| **Tính linh hoạt** | Rất linh hoạt, dễ dàng thay đổi lệnh khi chạy container. | Rất nghiêm ngặt, muốn ghi đè phải dùng flag `--entrypoint`. |
| **Trường hợp sử dụng** | Phù hợp cho container chạy ứng dụng (Web server, API, script cần đổi cấu hình). | Phù hợp khi biến container thành một "công cụ CLI" (Executable tool). |

### Exercise 2.3: Image size comparison
- Develop: 1.66GB
- Production: 236MB
- Difference: 85.8%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://confident-love-production-22b8.up.railway.app/
- Screenshot: https://github.com/vannguyen198/day12_ha-tang-cloud_va_deployment/blob/main/03-cloud-deployment/railway/responses.jpg

### Exercise 3.2: Comparison
| | railway.toml | render.yaml |
|-|-------------|-------------|
| Builder | Dockerfile | Docker |
| Start cmd | uvicorn với `$PORT` | Tự động từ Dockerfile CMD |
| Health check | `/health` path | `/health` path |
| Env vars | Set qua `railway variables set` | Định nghĩa trong YAML, secrets set qua dashboard |
| Region | Không chỉ định | Có chỉ định |
| Auto-deploy | Không | `autoDeploy: true` |
## Part 4: API Security

### Exercise 4.1-4.3: Test results
**API key check ở đâu?**
```python
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(status_code=401, ...)
    if api_key != API_KEY:
        raise HTTPException(status_code=403, ...)
    return api_key
```

**Nếu sai key:** trả về HTTP 403 Forbidden  
**Rotate key:** thay đổi env var `AGENT_API_KEY` và restart service

**Test results:**
```
# Không có key → 401
{"detail": "Missing API key. Include header: X-API-Key: <your-key>"}

# Có key đúng → 200
{"question": "hello", "answer": "..."}
```
### Exercise 4.2: JWT flow

1. Client POST `/auth/token` với username/password
2. Server verify credentials, tạo JWT với `{sub, role, iat, exp}`, ký bằng `SECRET_KEY` (HS256)
3. Client nhận token (hết hạn sau 60 phút)
4. Client gửi `Authorization: Bearer <token>` trong mỗi request
5. Server verify signature, extract user info → process request (không cần DB lookup)

**Ưu điểm:** Stateless — server không cần lưu session

### Exercise 4.3: Rate limiting

**Algorithm:** Sliding Window Counter  
**Limit:** User: 10 req/min | Admin: 100 req/min  
**Bypass cho admin:** Khác `RateLimiter` instance — `rate_limiter_admin = RateLimiter(max_requests=100, ...)`

**Test results:**
```
Request 1-9:  HTTP 200
Request 10:   HTTP 429 — "Rate limit exceeded"
              Headers: X-RateLimit-Remaining: 0, Retry-After: <seconds>

Admin requests 1-12: HTTP 200 (không bị block)
```

### Exercise 4.4: Cost guard implementation

```python
# Trong production/cost_guard.py
def check_budget(self, user_id: str) -> None:
        """
        Kiểm tra budget trước khi gọi LLM.
        Raise 402 nếu vượt budget.
        """
        record = self._get_record(user_id)

        # Global budget check
        if self._global_cost >= self.global_daily_budget_usd:
            logger.critical(f"GLOBAL BUDGET EXCEEDED: ${self._global_cost:.4f}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable due to budget limits. Try again tomorrow.",
            )

        # Per-user budget check
        if record.total_cost_usd >= self.daily_budget_usd:
            raise HTTPException(
                status_code=402,  # Payment Required
                detail={
                    "error": "Daily budget exceeded",
                    "used_usd": record.total_cost_usd,
                    "budget_usd": self.daily_budget_usd,
                    "resets_at": "midnight UTC",
                },
            )

        # Warning khi gần hết budget
        if record.total_cost_usd >= self.daily_budget_usd * self.warn_at_pct:
            logger.warning(
                f"User {user_id} at {record.total_cost_usd/self.daily_budget_usd*100:.0f}% budget"
            )
```
---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health và readiness checks

```python
@app.get("/health")
def health():
    """
    LIVENESS PROBE — "Agent có còn sống không?"

    Cloud platform (Railway, Render, K8s) gọi endpoint này định kỳ.
    Nếu trả về non-200 hoặc timeout → platform restart container.

    Nên trả về:
    - status: "ok" hoặc "degraded"
    - uptime: seconds
    - version: để biết đang chạy version nào
    """
    uptime = round(time.time() - START_TIME, 1)

    # Kiểm tra dependencies quan trọng
    checks = {}

    # Check memory (ví dụ đơn giản)
    try:
        import psutil
        mem = psutil.virtual_memory()
        checks["memory"] = {
            "status": "ok" if mem.percent < 90 else "degraded",
            "used_percent": mem.percent,
        }
    except ImportError:
        checks["memory"] = {"status": "ok", "note": "psutil not installed"}

    overall_status = "ok" if all(
        v.get("status") == "ok" for v in checks.values()
    ) else "degraded"

    return {
        "status": overall_status,
        "uptime_seconds": uptime,
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


@app.get("/ready")
def ready():
    """
    READINESS PROBE — "Agent có sẵn sàng nhận request chưa?"

    Load balancer dùng endpoint này để quyết định có route
    traffic vào instance này không.

    Trả về 503 khi:
    - Đang khởi động (model chưa load xong)
    - Đang shutdown
    - Database/dependencies chưa connect
    """
    if not _is_ready:
        raise HTTPException(
            status_code=503,
            detail="Agent not ready. Check back in a few seconds.",
        )
    return {
        "ready": True,
        "in_flight_requests": _in_flight_requests,
    }
```

**Khác biệt quan trọng:**
- `/health` = liveness: process còn sống? → Platform restart nếu fail
- `/ready` = readiness: có thể nhận request? → Load balancer stop routing nếu fail

### Exercise 5.2: Graceful shutdown

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    _is_ready = True
    yield
    # Shutdown phase
    _is_ready = False
    timeout = 30
    while _in_flight_requests > 0 and elapsed < timeout:
        time.sleep(1)  # Chờ request đang xử lý hoàn thành

signal.signal(signal.SIGTERM, handle_sigterm)
```

**Quan sát:** Khi SIGTERM được gửi, server dừng nhận request mới (`_is_ready = False`), nhưng chờ request đang xử lý hoàn thành (tối đa 30s) trước khi exit.

### Exercise 5.3: Stateless design

**Anti-pattern (stateful):**
```python
conversation_history = {}  # State trong memory của instance
```
→ Khi scale 3 instances, user A gửi request 1 tới instance 1, request 2 tới instance 2 → **mất session!**

**Correct (stateless với Redis):**
```python
def save_session(session_id, data):
    _redis.setex(f"session:{session_id}", 3600, json.dumps(data))

def load_session(session_id):
    data = _redis.get(f"session:{session_id}")
    return json.loads(data) if data else {}
```
→ Bất kỳ instance nào cũng đọc được session từ Redis → scale an toàn
Session được giữ qua nhiều turns.

### Exercise 5.4: Load balancing

Docker Compose scale:
```bash
docker compose up --scale agent=3
```
→ Nginx round-robin giữa 3 instances. Nếu 1 instance die (healthcheck fail), Nginx tự loại ra khỏi pool, traffic chuyển sang 2 instances còn lại.

### Exercise 5.5: Stateless test

Khi Redis available: conversation history persist dù request được serve bởi instance khác.  
Khi Redis không có (fallback in-memory): history chỉ tồn tại trong 1 instance — không stateless.

---

## Tổng kết

| Concept | Key lesson |
|---------|-----------|
| Localhost vs Production | Không bao giờ hardcode secrets; dùng env vars + 12-Factor |
| Docker | Multi-stage build: image nhỏ hơn 7.5x (56MB vs 424MB) |
| Cloud deployment | Push to GitHub → Render auto-deploy từ render.yaml |
| API Security | JWT stateless auth + Sliding window rate limit + Cost guard per user |
| Scaling | Stateless design (Redis session) + Health/Ready probes + Graceful shutdown |