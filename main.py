from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

class TextRequest(BaseModel):
    text: str

# 메인 페이지: 웹 화면 제공
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <body>
            <h2>PH Focus 엔진 테스트기</h2>
            <textarea id="inputText" placeholder="텍스트를 입력하세요"></textarea>
            <button onclick="analyzeText()">분석하기</button>
            <p>결과: <span id="result"></span></p>
            <script>
                async function analyzeText() {
                    const text = document.getElementById('inputText').value;
                    const res = await fetch('/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    const data = await res.json();
                    document.getElementById('result').innerText = data.enhanced;
                }
            </script>
        </body>
    </html>
    """

# API 로직
@app.post("/process")
def process_text(request: TextRequest):
    enhanced_text = request.text.replace("중요", "【중요】")
    return {"enhanced": enhanced_text}
