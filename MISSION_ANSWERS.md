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
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
[Paste your test outputs]

### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]