# Sensei Unified Self-Check System

## Tối giản hoá ứng dụng Python cho việc sinh đề thi và testcase

## Tính năng chính

### 1. Hệ thống tự động sinh đề
- **algebra**: Phương trình bậc nhất, bậc hai, phân tích nhân tử, hệ phương trình
- **geometry**: Tính diện tích tam giác, tròn và các hình học cơ bản

### 2. Tùy chỉnh API
- Có thể cấu hình endpoint API tùy chỉnh
- Hỗ trợ API key và rate limiting
- Timeout tùy chỉnh

### 3. Tự động sinh testcase
- Sinh testcase một cách thông minh dựa trên đề thi
- Hỗ trợ multiple_choice, short_answer, numerical

### 4. Kiểm tra tự động
- Xác thực đáp án chính xác với độ chính xác 0.0001
- Hỗ trợ kiểu dữ liệu khác nhau

## Cài đặt

```bash
pip install fastapi uvicorn pydantic pyyaml
```

## Sử dụng CLI

```bash
# Sinh bài thi đại số - dễ
python app.py generate --type multiple_choice --difficulty easy --topic linear_equation --count 5

# Sinh bài thi hình học - trung bình  
python app.py generate --type numerical --difficulty medium --topic circle --count 3

# Chạy API server
python app.py server --port 8000
```

## API Endpoints

| Phương thức | Endpoint | Mô tả |
|--------------|----------|-------|
| GET | / | Kiểm tra trạng thái |
| GET | /generators | Liệt kê các generator |
| POST | /generate/problem | Sinh đề thi mới |
| POST | /generate/testcase | Sinh testcase cho đề |
| POST | /configure/api | Cấu hình API tùy chỉnh |
| POST | /config | Alias cho configure |

## Ví dụ API

### Tạo đề thi
```bash
curl -X POST http://localhost:8000/generate/problem \
  -H "Content-Type: application/json" \
  -d '{
    "type": "multiple_choice",
    "difficulty": "easy",
    "topic": "linear_equation",
    "count": 5
  }'
```

### Cấu hình API tùy chỉnh
```bash
curl -X POST http://localhost:8000/configure/api \
  -H "Content-Type: application/json" \
  -d '{
    "generator": "algebra",
    "endpoint_url": "https://api.yourservice.com/v1",
    "api_key": "your_api_key_here",
    "timeout": 60,
    "rate_limit": 50
  }'
```

## Cấu trúc thư mục

```
Sensei_Unified/
├── app.py           # Ứng dụng chính
├── README.md        # Hướng dẫn
├── package.json     # Thông tin gói
├── requirements.txt # Dependencies
└── .gitignore       # Ignore files
```

## License

MIT License