"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import re
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"
        self._request_counts = {}

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu thời gian thực)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        request_count = self._request_counts.get(prompt, 0) + 1
        self._request_counts[prompt] = request_count
        
        # Mô phỏng nhận diện intent VinBus và trích xuất tham số cơ bản.
        if (
            "đăng ký vé tháng nếu" in prompt_lower
            and (request_count > 1 or "monthly_pass_available" in prompt_lower)
        ):
            name_match = re.search(r"tôi là\s+(.+?),\s*số điện thoại", prompt, re.IGNORECASE)
            phone_match = re.search(r"số điện thoại\s*([0-9]{9,11})", prompt, re.IGNORECASE)
            return {
                "type": "tool_call",
                "tool_name": "register_monthly_pass",
                "arguments": {
                    "full_name": name_match.group(1).strip() if name_match else "Nguyễn Minh Anh",
                    "phone": phone_match.group(1) if phone_match else "0901234567",
                    "route_id": "VB02"
                },
                "thought": "Tuyến VB02 hỗ trợ vé tháng. Tôi sẽ tiếp tục đăng ký vé tháng cho khách hàng."
            }

        if "tìm tuyến" in prompt_lower or "lộ trình" in prompt_lower or "đi từ" in prompt_lower:
            if "sân bay tân sơn nhất" in prompt_lower:
                origin = "Sân bay Tân Sơn Nhất"
                destination = "Điểm không có trong mạng lưới VinBus"
            elif "landmark 81" in prompt_lower and "đại học quốc gia" in prompt_lower:
                origin = "Landmark 81"
                destination = "Đại học Quốc gia TP.HCM"
            else:
                origin = "Vinhomes Central Park"
                destination = "Bến xe Miền Đông mới"

            return {
                "type": "tool_call",
                "tool_name": "route_query",
                "arguments": {"origin": origin, "destination": destination},
                "thought": f"Người dùng cần tra cứu lộ trình từ {origin} đến {destination}. Tôi sẽ gọi tool route_query."
            }

        if "điều kiện đăng ký" in prompt_lower or "giá vé" in prompt_lower:
            return {
                "type": "text",
                "content": "VinBus hỗ trợ thông tin vé tháng và điều kiện đăng ký. Bạn có thể cung cấp tuyến muốn sử dụng để tiếp tục đăng ký.",
                "thought": "Câu hỏi chung về vé tháng, trả lời trực tiếp không cần gọi Tool."
            }

        if "đăng ký" in prompt_lower and "vé tháng" in prompt_lower:
            name_match = re.search(r"tên\s+(.+?),\s*số điện thoại", prompt, re.IGNORECASE)
            phone_match = re.search(r"(?:số điện thoại|sđt)\s*([0-9]{9,11})", prompt, re.IGNORECASE)
            route_match = re.search(r"tuyến\s+(VB\d+)", prompt, re.IGNORECASE)

            full_name = name_match.group(1).strip() if name_match else "Nguyễn Minh Anh"
            phone = phone_match.group(1) if phone_match else "0901234567"
            route_id = route_match.group(1).upper() if route_match else "VB01"

            return {
                "type": "tool_call",
                "tool_name": "register_monthly_pass",
                "arguments": {"full_name": full_name, "phone": phone, "route_id": route_id},
                "thought": f"Người dùng muốn đăng ký vé tháng tuyến {route_id}. Tôi sẽ gọi tool register_monthly_pass."
            }

        if "vé tháng" in prompt_lower:
            return {
                "type": "text",
                "content": "VinBus hỗ trợ thông tin vé tháng và điều kiện đăng ký. Bạn có thể cung cấp tuyến muốn sử dụng để tiếp tục đăng ký.",
                "thought": "Câu hỏi chung về vé tháng, trả lời trực tiếp không cần gọi Tool."
            }

        return {
            "type": "text",
            "content": "Tôi có thể hỗ trợ tra cứu lộ trình VinBus hoặc đăng ký vé tháng.",
            "thought": "Chưa có đủ thông tin để gọi Tool VinBus."
        }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-3.6-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("[Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
