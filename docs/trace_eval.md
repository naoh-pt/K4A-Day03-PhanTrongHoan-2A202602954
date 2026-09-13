# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Phan Trọng Hoàn 
> **Mã Sinh Viên / Mã Học viên:** 2A202602954  
> **Chủ đề Lựa chọn:** Trợ lý Dịch vụ Khách hàng VinBus: Tra cứu lộ trình tuyến xe bus điện và đăng ký vé tháng.

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 5/ 5 | Một yêu cầu có thể cần nhiều bước: xác định tuyến, kiểm tra điểm đi và điểm đến, tìm chuyến phù hợp, sau đó tư vấn hoặc đăng ký vé tháng. |
| **2. Tool Interaction** | 5/ 5 | Agent cần gọi các công cụ tra cứu tuyến xe, điểm dừng, lịch chạy và đăng ký vé tháng. |
| **3. Dynamic Decision** | 5/ 5 | Hành động tiếp theo phụ thuộc vào kết quả tra cứu trước đó. Ví dụ, nếu tuyến không đi qua điểm đến, Agent phải tìm tuyến thay thế. |
| **4. Long Horizon Goal** | 4/ 5 | Mục tiêu có thể kéo dài qua nhiều bước, đặc biệt khi người dùng vừa cần tìm lộ trình vừa đăng ký vé |
| **TỔNG ĐIỂM AGENTIC FIT** | **19/ 20** | *Chủ đề phù hợp để triển khai ReAct Agent.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dưới đây là đoạn trace VinBus tiêu biểu từ file `docs/trace_waterfall.json`, được tạo bằng Gemini API thật.

```json
[
  {
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "route_query",
    "arguments": {
      "origin": "Vinhomes Central Park",
      "destination": "Bến xe Miền Đông mới"
    },
    "observation": {
      "status": "SUCCESS",
      "route_id": "VB01",
      "data": {
        "route_name": "Vinhomes Central Park - Bến xe Miền Đông mới",
        "estimated_minutes": 35,
        "next_departure": "08:30"
      }
    },
    "latency_ms": 1874.82
  },
  {
    "step": 2,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "register_monthly_pass",
    "arguments": {
      "full_name": "Nguyễn Minh Anh",
      "phone": "0901234567",
      "route_id": "VB01"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "MP-0901234567-VB01"
    },
    "latency_ms": 2732.63
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên Gemini API thật.
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server:** 5 lượt.
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
