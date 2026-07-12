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
            <div id="result" style="font-size: 20px; border: 1px solid #ccc; padding: 10px; margin-top: 20px; min-height: 50px;"></div>
            
            <script>
            async function processText() {
                const text = document.getElementById("inputText").value;
                const resultDiv = document.getElementById("result");
                
                // 1. 요청 시작: 로딩 애니메이션과 텍스트를 즉시 표시
                resultDiv.innerHTML = '<div class="spinner"></div>문자를 분석하여 재구성중...';
                
                try {
                    const response = await fetch("/process", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({text: text})
                    });
                    const data = await response.json();
                    
                    // 2. 결과 수신 후: 텍스트를 결과값으로 덮어씀
                    resultDiv.innerHTML = data.result;
                } catch (e) {
                    resultDiv.innerHTML = "분석 오류가 발생했습니다.";
                }
            }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    prompt = (
        f"입력된 문장의 오탈자를 교정하고, 각 단어의 중요도를 1~100으로 평가하세요.\n"
        f"반드시 아래 JSON 형식으로만 응답하세요.\n"
        f"{{\"corrected\": \"교정된 문장\", \"scores\": {{\"단어\": 90, \"단어\": 10}}}}\n\n"
        f"문장: {request.text}"
    )
    
    try:
        response = model.generate_content(prompt)
        start = response.text.find('{')
        end = response.text.rfind('}') + 1
        data = json.loads(response.text[start:end])
        
        corrected_text = data.get("corrected", request.text)
        scores = data.get("scores", {})
        
        # HTML <b> 태그 적용
        result_words = []
        for word in corrected_text.split():
            clean_word = word.strip(".,!?")
            if scores.get(clean_word, 0) >= 90:
                result_words.append(f"<b>{word}</b>")
            else:
                result_words.append(word)
                
        return {"result": " ".join(result_words)}
    except Exception as e:
        return {"result": "분석 오류가 발생했습니다."}
