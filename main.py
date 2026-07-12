import os
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
            <h2>PH Focus Engine</h2>
            <textarea id="inputText" rows="4" cols="50" placeholder="알림 문구를 입력하세요"></textarea><br>
            <button onclick="processText()">가독성 개선하기</button>
            <div id="result" style="font-size: 20px; font-weight: bold; border: 1px solid #ccc; padding: 10px; white-space: pre-wrap; margin-top: 20px;"></div>
            
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
    # '글자 변경 금지'를 위해 구체적 지시를 추가
    prompt = (
        f"원본 텍스트에서 글자, 공백, 줄바꿈을 단 하나도 변경하지 마십시오.\n"
        f"반드시 원본 그대로 유지한 상태에서, 중요한 키워드에만 **(볼드체) 서식을 입히세요.\n"
        f"추가적인 설명이나 글자 변형은 절대 금지합니다.\n\n"
        f"원본 텍스트:\n{request.text}"
    )
    
    def generate():
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    return StreamingResponse(generate(), media_type="text/plain")
