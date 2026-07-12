from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import re

app = FastAPI()

class TextRequest(BaseModel):
    text: str

# 중요 키워드 선정 로직 (AI의 기초 단계)
def enhance_text_with_ai(text: str):
    # 강조할 단어 목록 (나중에 AI 모델로 확장 가능)
    keywords = ["중요", "긴급", "회의", "확인", "필수", "이벤트", "할인"]
    
    enhanced = text
    for word in keywords:
        # 단어가 포함되어 있다면 대괄호를 씌움
        if word in enhanced:
            enhanced = enhanced.replace(word, f"【{word}】")
    return enhanced

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2>PH Focus AI 엔진 (v2.0)</h2>
            <textarea id="inputText" style="width:100%; height:100px;"></textarea><br>
            <button onclick="analyzeText()" style="padding: 10px 20px; margin-top:10px;">분석하기</button>
            <p><strong>결과:</strong> <span id="result" style="font-weight:bold; color:#d9534f;"></span></p>
            <script>
                async function analyzeText() {
                    const text = document.getElementById('inputText').value;
                    const res = await fetch('/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    const data = await res.json();
                    document.getElementById('result').innerText = data.enhanced;
                }
            </script>
        </body>
    </html>
    """

@app.post("/process")
def process_text(request: TextRequest):
    enhanced = enhance_text_with_ai(request.text)
    return {"enhanced": enhanced}

import openai # OpenAI 라이브러리 필요

# AI가 핵심 단어를 추출하게 하는 함수
def extract_keywords_with_ai(text: str):
    client = openai.OpenAI(api_key="본인의_API_키")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 텍스트 가독성 전문가야. 입력된 문장에서 가장 중요한 키워드 3개를 뽑아서 콤마(,)로 구분해줘."},
            {"role": "user", "content": text}
        ]
    )
    # AI가 뽑아준 단어들을 리스트로 변환
    keywords = response.choices[0].message.content.split(',')
    return [k.strip() for k in keywords]

