import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# API 키 설정
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
# 작동이 확인된 모델 사용
model = genai.GenerativeModel('gemini-3.5-flash')

class TextRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <html>
        <body>
            <h2>PH Focus Engine (실시간 강조)</h2>
            <textarea id="inputText" rows="4" cols="50" placeholder="알림 문구를 입력하세요"></textarea><br>
            <button onclick="processText()">가독성 개선하기</button>
            <div id="result" style="font-size: 20px; font-weight: bold; border: 1px solid #ccc; padding: 10px; white-space: pre-wrap; margin-top: 20px;"></div>
            
            <script>
            async function processText() {
                const text = document.getElementById("inputText").value;
                const resultDiv = document.getElementById("result");
                resultDiv.innerHTML = "분석 및 강조 중...";
                
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
                    
                    const chunk = decoder.decode(value);
                    // 들어온 마크다운 문자열을 HTML 태그로 즉시 변환하여 표시
                    const formattedChunk = chunk.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>');
                    resultDiv.innerHTML += formattedChunk;
                }
            }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    def generate():
        # AI에게 점수 매기기 요청
        prompt = (
            f"입력된 문장의 각 단어들의 중요도를 1~100 사이의 점수로 평가하세요.\n"
            f"반드시 원문 텍스트를 수정(삭제, 추가, 변경)하지 말고, 단어별 점수만 JSON 형식으로 반환하세요.\n"
            f"출력 예시: {{\"박훈\": 95, \"님\": 10, \"오세요\": 85}}\n\n"
            f"문장: {request.text}"
        )
        
        try:
            response = model.generate_content(prompt)
            start = response.text.find('{')
            end = response.text.rfind('}') + 1
            scores = json.loads(response.text[start:end])
        except:
            yield request.text
            return

        words = request.text.split()
        for i, word in enumerate(words):
            # 문장 부호를 제외하고 점수 검색
            clean_word = word.strip(".,!?")
            score = scores.get(clean_word, 0)
            
            # 볼드체 마크다운 적용
            if score >= 90:
                chunk = f"**{word}**"
            else:
                chunk = word
            
            # 공백 유지하며 스트리밍 전송
            yield chunk + (" " if i < len(words) - 1 else "")

    return StreamingResponse(generate(), media_type="text/event-stream")
