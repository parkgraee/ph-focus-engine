from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# Google API 키 설정
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name='gemini-1.5-flash-8b')


class TextRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <html>
        <body>
            <h2>PH Focus Engine (Gemini 가독성 개선)</h2>
            <textarea id="inputText" rows="4" cols="50" placeholder="알림 문구를 입력하세요"></textarea><br>
            <button onclick="processText()">가독성 개선하기</button>
            <p>결과:</p>
            <div id="result" style="font-size: 20px; font-weight: bold; border: 1px solid #ccc; padding: 10px; white-space: pre-wrap;"></div>
            
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

@app.post("/process")
def process_text(request: TextRequest):
    try:
        prompt = f"당신은 가독성 전문가입니다. 다음 문구의 핵심 키워드를 찾아내고, 특수문자나 줄바꿈을 활용하여 눈에 띄게 재구성하세요. 설명은 생략하고 결과물만 출력하세요: {request.text}"
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"result": f"오류 발생: {str(e)}"}
