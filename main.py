from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# 환경 변수에서 API 키를 안전하게 불러옵니다
# client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# 수정 전
# client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 수정 후 (아래 줄을 그대로 복사해서 붙여넣으세요)
client = openai.OpenAI(api_key="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")


class TextRequest(BaseModel):
    text: str
    
# AI가 핵심 단어를 추출하는 함수
def extract_keywords_with_ai(text: str):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 텍스트 가독성 전문가야. 입력된 문장에서 가장 중요한 키워드 3개를 뽑아서 콤마(,)로만 구분해줘. 다른 말은 절대 하지 마."},
                {"role": "user", "content": text}
            ]
        )
        keywords = response.choices[0].message.content.split(',')
        return [k.strip() for k in keywords]
    except Exception as e:
        print(f"AI 호출 오류: {e}")
        return []

@app.post("/process")
def process_text(request: TextRequest):
    # AI로 키워드 추출
    keywords = extract_keywords_with_ai(request.text)
    
    # 추출된 키워드에 강조 적용
    enhanced = request.text
    for word in keywords:
        if word and word in enhanced:
            enhanced = enhanced.replace(word, f"【{word}】")
            
    return {"enhanced": enhanced}

# HTML 생략 (이전과 동일하게 유지)
# 재배포 테스
