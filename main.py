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
        <style>
            .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; 
                       width: 30px; height: 30px; animation: spin 1s linear infinite; 
                       display: inline-block; vertical-align: middle; margin-right: 10px; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
        <body>
            <h2>PH Focus Engine</h2>
            <textarea id="inputText" rows="4" cols="50" placeholder="문구를 입력하세요"></textarea><br>
            <button onclick="processText()">가독성 개선하기</button>
            <div id="result" style="font-size: 20px; border: 1px solid #ccc; padding: 10px; margin-top: 20px;"></div>
            
            <script>
            async function processText() {
                const text = document.getElementById("inputText").value;
                const resultDiv = document.getElementById("result");
                resultDiv.innerHTML = '<div class="spinner"></div>문자를 분석하여 재구성중...';
                
                const response = await fetch("/process", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text: text})
                });
                const data = await response.json();
                resultDiv.innerHTML = data.result;
            }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    # AI에게 교정 및 점수 데이터만 요청
    prompt = (
        f"1. 다음 문장의 오탈자와 띄어쓰기를 교정하세요.\n"
        f"2. 교정된 문장의 각 단어별 중요도를 1~100 점수로 매기세요.\n"
        f"3. 반드시 아래 JSON 형식으로만 응답하세요.\n"
        f"{{\"corrected\": \"교정된 문장\", \"scores\": {{\"단어1\": 점수, \"단어2\": 점수}}}\n\n"
        f"문장: {request.text}"
    )
    
    response = model.generate_content(prompt)
    try:
        start = response.text.find('{')
        end = response.text.rfind('}') + 1
        data = json.loads(response.text[start:end])
        corrected_text = data["corrected"]
        scores = data["scores"]
    except:
        return {"result": "분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}

    # 코드에서 직접 볼드체 적용 (90점 이상)
    result_words = []
    for word in corrected_text.split():
        clean_word = word.strip(".,!?")
        score = scores.get(clean_word, 0)
        if score >= 90:
            result_words.append(f"<b>{word}</b>")
        else:
            result_words.append(word)
            
    return {"result": " ".join(result_words)}
