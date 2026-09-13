"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    # {
    #     "name": "academic_query",
    #     "description": "Tra cứu hồ sơ và thông tin học vụ của sinh viên VinUni bằng mã sinh viên.",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             "student_id": {
    #                 "type": "string",
    #                 "description": "Mã sinh viên cần tra cứu (ví dụ: 'SV2026001')"
    #             }
    #         },
    #         "required": ["student_id"]
    #     }
    # },
    
    # # --------------------------------------------------------------------------
    # # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'schedule_appointment'
    # # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # # 1. Tool dùng để đặt lịch hẹn tư vấn học vụ với Cố vấn học tập VinUni.
    # # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    # #    - student_id (string): Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')
    # #    - datetime_str (string): Thời gian hẹn (ví dụ: '14:00 15/09/2026')
    # #    - advisor_name (string): Tên cố vấn học tập
    # # 3. Khai báo danh sách các trường bắt buộc (required).
    # # --------------------------------------------------------------------------
    # {
    #     "name": "schedule_appointment",
    #     "description": "Đặt lịch hẹn tư vấn học vụ với Cố vấn học tập VinUni.",
    #     "parameters": {
    #         "type": "object",
    #         "properties": {
    #             # TODO 1.2: Khai báo các thuộc tính tham số cho Tool tại đây...
    #         },
    #         "required": [] # TODO 1.2: Khai báo danh sách các trường bắt buộc tại đây...
    #     }
    # }
    {
        "name": "route_query",
        "description": "Tra cứu lộ trình VinBus giữa điểm đi và điểm đến.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Điểm xuất phát của hành khách."
                },
                "destination": {
                    "type": "string",
                    "description": "Điểm đến của hành khách."
                }
            },
            "required": ["origin", "destination"]
        }
    },
    {
        "name": "register_monthly_pass",
        "description": "Đăng ký vé tháng VinBus cho hành khách.",
        "parameters": {
            "type": "object",
            "properties": {
                "full_name": {
                    "type": "string",
                    "description": "Họ và tên hành khách."
                },
                "phone": {
                    "type": "string",
                    "description": "Số điện thoại hành khách."
                },
                "route_id": {
                    "type": "string",
                    "description": "Mã tuyến VinBus muốn đăng ký."
                }
            },
            "required": ["full_name", "phone", "route_id"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "VB01": {
        "route_name": "Vinhomes Central Park - Bến xe Miền Đông mới",
        "stops": ["Vinhomes Central Park", "Landmark 81", "Bến xe Miền Đông mới"],
        "estimated_minutes": 35,
        "next_departure": "08:30",
        "monthly_pass_available": True
    },
    "VB02": {
        "route_name": "Landmark 81 - Đại học Quốc gia TP.HCM",
        "stops": ["Landmark 81", "Xa lộ Hà Nội", "Đại học Quốc gia TP.HCM"],
        "estimated_minutes": 50,
        "next_departure": "09:00",
        "monthly_pass_available": True
    }
}


def execute_route_query(origin: str, destination: str) -> str:
    """Tra cứu tuyến VinBus phù hợp với điểm đi và điểm đến."""
    normalized_origin = origin.strip().lower()
    normalized_destination = destination.strip().lower()

    for route_id, route in MOCK_DATABASE.items():
        normalized_stops = [stop.lower() for stop in route["stops"]]
        if normalized_origin in normalized_stops and normalized_destination in normalized_stops:
            return json.dumps({
                "status": "SUCCESS",
                "route_id": route_id,
                "origin": origin,
                "destination": destination,
                "data": route
            }, ensure_ascii=False)

    return json.dumps({
        "status": "NOT_FOUND",
        "message": f"Không tìm thấy tuyến VinBus phù hợp từ '{origin}' đến '{destination}'."
    }, ensure_ascii=False)


def execute_register_monthly_pass(full_name: str, phone: str, route_id: str) -> str:
    """Đăng ký vé tháng VinBus cho hành khách."""
    normalized_route_id = route_id.strip().upper()
    route = MOCK_DATABASE.get(normalized_route_id)

    if not route:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy tuyến VinBus có mã '{route_id}'."
        }, ensure_ascii=False)

    if not route["monthly_pass_available"]:
        return json.dumps({
            "status": "UNAVAILABLE",
            "message": f"Tuyến '{normalized_route_id}' hiện chưa hỗ trợ đăng ký vé tháng."
        }, ensure_ascii=False)

    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"MP-{phone}-{normalized_route_id}",
        "full_name": full_name,
        "phone": phone,
        "route_id": normalized_route_id,
        "message": f"Đăng ký vé tháng thành công cho {full_name} trên tuyến {normalized_route_id}."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "route_query": execute_route_query,
    "register_monthly_pass": execute_register_monthly_pass
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
