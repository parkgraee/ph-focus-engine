from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# Google API 키 설정
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-3.5-flash')


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
       
       prompt = (
            f"당신은 가독성 전문가입니다. 다음 문장의 원문을 수정하지 않고 오직 서식(볼드체)만 적용하여 가독성을 높이세요.\n"
            f"절대 준수 규칙:\n"
            f"1. 글자 수 100% 보존: 공백 포함 원문 글자 수와 똑같아야 합니다.\n"
            f"2. 추가/삭제 금지: 단 한 글자도 추가하거나 삭제하지 마세요.\n"
            f"3. 가독성 강조: 중요한 키워드에만 **볼드체**를 적용하세요.\n"
            f"원문: {request.text}"
        ) 
        
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"result": f"오류 발생: {str(e)}"}
