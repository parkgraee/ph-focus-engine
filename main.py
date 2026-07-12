import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# 기존 API 키 설정 유지
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# 현재 잘 작동 중인 모델 설정 유지
model = genai.GenerativeModel('gemini-3.5-flash')

class TextRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <html>
        <body>
            <h2>PH Focus Engine (가독성 개선)</h2>
            <textarea id="inputText" rows="4" cols="50" placeholder="알림 문구를 입력하세요"></textarea><br>
            <button onclick="processText()">가독성 개선하기</button>
            <p>결과:</p>
            <div id="result" style="font-size: 20px; font-weight: bold; border: 1px solid #ccc; padding: 10px; white-space: pre-wrap;"></div>
            
            <script>
            async function processText() {
                const text = document.getElementById("inputText").value;
                const resultDiv = document.getElementById("result");
                resultDiv.innerText = "처리 중...";
                
                const response = await fetch("/process", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({text: text})
                });
                
                // 스트리밍 응답 처리를 위한 로직
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
    # 시스템 프롬프트: 글자 수 고정 및 변형 금지 규칙을 최우선으로 강화
    prompt = (
        f"당신은 가독성 편집기입니다. 다음 규칙을 엄격히 준수하여 원문을 출력하세요.\n\n"
        f"규칙:\n"
        f"1. 글자 수 100% 보존: 공백 포함 원문 글자 수와 결과물의 글자 수는 100% 동일해야 함.\n"
        f"2. 추가/삭제 금지: 단 한 글자도 추가하거나 삭제하지 마세요.\n"
        f"3. 변형 금지: 단어 순서, 조사, 문장 부호는 절대 변경하지 마세요.\n"
        f"4. 오직 강조: 원문의 특정 단어에만 **볼드체**를 적용하세요.\n"
        f"5. 부가 설명 금지: 오직 결과물 텍스트만 출력하세요.\n\n"
        f"원문: {request.text}"
    )
    
    # 스트리밍 방식 적용: AI 응답을 즉시 웹 화면으로 전달
    def generate():
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    return StreamingResponse(generate(), media_type="text/plain")
