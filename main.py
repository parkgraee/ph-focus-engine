import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-3.5-flash')

class TextRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <html>
        <body>
            <h2>PH Focus Engine</h2>
            <textarea id="inputText" rows="4" cols="50"></textarea><br>
            <button id="btn" onclick="process()">가독성 개선하기</button>
            <div id="result" style="font-size: 20px; border: 1px solid #ccc; padding: 10px; margin-top: 20px;"></div>
            
            <script>
            async function process() {
                const text = document.getElementById("inputText").value;
                const div = document.getElementById("result");
                div.innerHTML = "🔄 분석 및 재구성 중...";
                
                const res = await fetch("/process", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text: text})
                });
                const data = await res.json();
                div.innerHTML = data.result;
            }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    prompt = f"문장 '{request.text}'의 오탈자를 교정하고, 중요 단어(90점 이상)를 <b>태그로 감싸세요. JSON: {{\"result\": \"교정된 문장(태그 포함)\"}}"
    try:
        response = model.generate_content(prompt)
        start = response.text.find('{')
        end = response.text.rfind('}') + 1
        data = json.loads(response.text[start:end])
        return {"result": data.get("result", "오류 발생")}
    except:
        return {"result": "분석 실패"}
