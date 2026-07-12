from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# 환경 변수에서 API 키를 가져옵니다.
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TextRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <html>
        <body>
            <h2>PH Focus Engine (AI 가독성 개선)</h2>
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
        # OpenAI를 사용하여 텍스트 가독성 최적화 요청
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 텍스트 가독성 전문가입니다. 주어진 문구에서 핵심 키워드를 찾아내고, 특수문자나 줄바꿈을 활용하여 눈에 띄게 재구성하세요. 설명은 생략하고 결과물만 출력하세요."},
                {"role": "user", "content": request.text}
            ]
        )
        optimized_text = response.choices[0].message.content
        return {"result": optimized_text}
    except Exception as e:
        return {"result": f"오류 발생: {str(e)}"}
