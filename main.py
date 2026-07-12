import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
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
            <h2>PH Focus Engine (교정 및 강조)</h2>
            <textarea id="inputText" rows="4" cols="50" placeholder="문구를 입력하세요"></textarea><br>
            <button onclick="processText()">가독성 개선하기</button>
            <div id="result" style="font-size: 20px; font-weight: bold; border: 1px solid #ccc; padding: 10px; white-space: pre-wrap; margin-top: 20px;"></div>
            
            <script>
            async function processText() {
                const text = document.getElementById("inputText").value;
                const resultDiv = document.getElementById("result");
                resultDiv.innerHTML = "분석 중...";
                const response = await fetch("/process", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text: text})
                });
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                resultDiv.innerHTML = "";
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    resultDiv.innerHTML += decoder.decode(value);
                }
            }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    def generate():
        # AI에게 오탈자 수정 후 점수 매기기 요청
        prompt = (
            f"1. 먼저 다음 문장의 오탈자와 띄어쓰기를 완벽하게 교정하세요.\n"
            f"2. 교정된 문장의 각 단어별 중요도를 1~100 점수로 매기세요.\n"
            f"3. 반드시 아래 JSON 형식으로만 응답하세요.\n"
            f"{{\"corrected\": \"교정된 문장 전체\", \"scores\": {{\"단어1\": 95, \"단어2\": 10}}}}\n\n"
            f"문장: {request.text}"
        )
        
        response = model.generate_content(prompt)
        try:
            start = response.text.find('{')
            end = response.text.rfind('}') + 1
            data = json.loads(response.text[start:end])
            corrected = data["corrected"]
            scores = data["scores"]
        except:
            yield "분석 실패"
            return

        # 원문 재조립 (코드에서 직접 처리)
        words = corrected.split()
        for i, word in enumerate(words):
            clean_word = word.strip(".,!?")
            score = scores.get(clean_word, 0)
            
            # 90점 이상만 강조, 나머지는 평문
            if score >= 90:
                yield f"<b>{word}</b>" + (" " if i < len(words) - 1 else "")
            else:
                yield f"{word}" + (" " if i < len(words) - 1 else "")

    return StreamingResponse(generate(), media_type="text/event-stream")
