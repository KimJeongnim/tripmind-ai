import os
import json
from http.server import BaseHTTPRequestHandler
from google import genai


def generate_recommendation(data):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")

    if not data.get("date"):
        raise ValueError("여행 날짜를 입력해주세요.")

    if not data.get("style"):
        raise ValueError("여행 스타일을 선택해주세요.")

    if not data.get("companion"):
        raise ValueError("여행 동반자를 선택해주세요.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
당신은 국내 여행 전문 AI 플래너입니다.

사용자의 여행 정보를 바탕으로 국내 여행지를 1곳 추천해주세요.

여행 날짜: {data["date"]}
여행 스타일: {data["style"]}
여행 동반자: {data["companion"]}
추가 요청: {data.get("request", "") or "없음"}

다음 JSON 형식으로만 답변하세요.

{{
    "recommended_city": "추천 국내 여행지",
    "weather": "여행 시기의 일반적인 날씨 설명",
    "events": [
        "추천 관광 포인트 1",
        "추천 관광 포인트 2"
    ],
    "reason": "이 여행지를 추천하는 이유를 2~4문장으로 설명"
}}

조건:
- 국내 여행지만 추천합니다.
- 여행 날짜, 여행 스타일, 동반자를 고려합니다.
- recommended_city는 1곳만 작성합니다.
- events는 1~3개 작성합니다.
- JSON만 출력합니다.
- Markdown 코드 블록을 사용하지 않습니다.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            result = generate_recommendation(data)

            response_body = json.dumps(
                result,
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.end_headers()
            self.wfile.write(response_body)

        except ValueError as e:
            self.send_json_error(400, str(e))

        except Exception as e:
            print("API 오류:", e)
            self.send_json_error(
                500,
                "AI 추천 처리 중 오류가 발생했습니다."
            )

    def do_GET(self):
        self.send_json_error(
            405,
            "이 API는 POST 요청만 지원합니다."
        )

    def send_json_error(self, status_code, message):
        response_body = json.dumps(
            {"error": message},
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(response_body)