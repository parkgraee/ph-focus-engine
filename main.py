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
    # 1. AI에게 점수 매기기 요청 (중요도 점수만 JSON으로)
    prompt = (
        f"입력된 문장의 각 단어들의 중요도를 1~100 사이의 점수로 평가하세요.\n"
        f"절대 원문 텍스트를 수정하지 말고, 단어별 점수만 JSON 형식으로 반환하세요.\n"
        f"반환 예시: {{\"박훈\": 95, \"님\": 10, \"오세요\": 85}}\n\n"
        f"문장: {request.text}"
    )
    
    # 2. 스트리밍 처리를 위한 제너레이터 함수
    def generate():
        response = model.generate_content(prompt)
        
        # JSON 파싱 (AI 응답에서 { } 사이 값만 추출)
        try:
            start = response.text.find('{')
            end = response.text.rfind('}') + 1
            scores = json.loads(response.text[start:end])
        except:
            yield "분석 오류 발생"
            return

        # 원문 기반으로 결과물 생성 (직접 문자열 조합)
        words = request.text.split()
        for word in words:
            clean_word = word.strip(".,!?")
            score = scores.get(clean_word, 0)
            
            # 90점 이상만 볼드 처리
            if score >= 90:
                yield f"**{word}** "
            else:
                yield f"{word} "

    return StreamingResponse(generate(), media_type="text/plain")
