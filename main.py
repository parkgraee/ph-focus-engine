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
    text = request.text
    # 예시: '박훈'이라는 단어를 찾아서 강조 표시(★)를 붙여줍니다.
    if "박훈" in text:
        text = text.replace("박훈", "【★ 박훈 ★】")
    
    return {"result": text}
