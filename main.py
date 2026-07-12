from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI()

# 사용자가 보낼 데이터 형식
class TextRequest(BaseModel):
    text: str

# 1. 웹 화면(HTML)을 보여주는 페이지
@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <html>
        <body>
            <h2>PH Focus Engine 테스트</h2>
            <textarea id="inputText" rows="4" cols="50" placeholder="변환할 알림 문구를 입력하세요"></textarea><br>
            <button onclick="processText()">변환하기</button>
            <p>결과:</p>
            <div id="result" style="font-size: 20px; font-weight: bold; border: 1px solid #ccc; padding: 10px;"></div>
            
            <script>
            async function processText() {
                const text = document.getElementById("inputText").value;
                const response = await fetch("/process", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text: text})
                });
                const data = await response.json();
                document.getElementById("result").innerText = data.result;
            }
            </script>
        </body>
    </html>
    """

# 2. 텍스트 변환 로직 (API)
@app.post("/process")
def process_text(request: TextRequest):
    # 여기서 특수문자 변환 로직을 구현하세요 (현재는 예시)
    original_text = request.text
    # 간단한 변환 예시: '파트너님'이라는 글자가 있으면 대문자/특수문자 처리
    transformed = original_text.replace("파트너님", "【ＰＡＲＴＮＥＲ】")
    return {"result": transformed}
