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
                
                // 스트리밍 응답을 읽기 위한 Reader 생성
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                resultDiv.innerText = ""; // '처리 중...' 문구 삭제
                
                // 서버가 보내주는 조각(chunk)을 실시간으로 화면에 추가
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break; // 응답 종료 시 루프 탈출
                    const chunkText = decoder.decode(value);
                    resultDiv.innerText += chunkText; // 실시간 텍스트 추가
                }
            }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    # 핵심: AI가 문장을 건드리지 못하게 '강조만 수행'하도록 프롬프트 수정
    prompt = (
        f"당신은 텍스트 편집기입니다. 아래 원문에서 글자, 공백, 줄바꿈을 절대 수정하지 마세요.\n"
        f"오직 중요한 단어의 앞뒤에만 ** 기호를 추가하여 강조하세요.\n\n"
        f"절대 원칙:\n"
        f"1. 글자 수와 공백, 줄바꿈은 원문과 100% 동일해야 함 (단 한 글자도 추가/삭제/변경 금지).\n"
        f"2. 문장 구조나 단어 순서도 원문과 완전히 동일해야 함.\n"
        f"3. 오직 키워드에만 **(볼드체) 마크다운을 씌우는 작업만 수행.\n\n"
        f"원문:\n{request.text}\n\n"
        f"결과물(위 원문과 글자 수/구조 동일하게 출력):"
    )
    
    def generate():
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    return StreamingResponse(generate(), media_type="text/plain")
