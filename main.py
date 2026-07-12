import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
# 현재 잘 작동한다는 모델명 사용
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
                resultDiv.innerText = "분석 및 강조 중...";
                
                // 서버에 요청
                const response = await fetch("/process", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text: text})
                });
                
                // 스트리밍 데이터 읽기
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                resultDiv.innerText = "";
                
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    resultDiv.innerText += decoder.decode(value);
                }
            }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    # AI에게 점수만 매기도록 다시 한번 강력하게 요청
    prompt = (
        f"입력된 문장의 각 단어들의 중요도를 1~100 사이의 점수로 평가하세요.\n"
        f"절대 원문 텍스트를 수정(삭제, 추가, 변경)하지 마세요.\n"
        f"오직 단어와 점수 쌍으로 이루어진 JSON 형식만 출력하세요.\n"
        f"반환 예시: {{\"자\": 10, \"이것\": 95, \"이\": 10}}\n\n"
        f"문장: {request.text}"
    )
    
    def generate():
        response = model.generate_content(prompt)
        
        try:
            # AI 응답에서 JSON 부분만 추출
            start = response.text.find('{')
            end = response.text.rfind('}') + 1
            scores = json.loads(response.text[start:end])
        except:
            yield request.text # 오류 시 원문 그대로 반환
            return

        # 원문 기반으로 결과물 생성 (공백 유지)
        words = request.text.split()
        for i, word in enumerate(words):
            clean_word = word.strip(".,!?")
            score = scores.get(clean_word, 0)
            
            # 볼드체 처리
            if score >= 90:
                result_word = f"**{word}**"
            else:
                result_word = word
                
            # 단어 사이에만 공백 추가
            if i < len(words) - 1:
                yield result_word + " "
            else:
                yield result_word

    return StreamingResponse(generate(), media_type="text/plain")
