from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# 환경 변수를 통해 키를 로드합니다.
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TextRequest(BaseModel):
    text: str

@app.post("/process")
def process_text(request: TextRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 텍스트 가독성 전문가야. 입력된 문장에서 가장 중요한 키워드 3개를 뽑아서 콤마로만 구분해줘."},
                {"role": "user", "content": request.text}
            ]
        )
        keywords = [k.strip() for k in response.choices[0].message.content.split(',')]
        
        enhanced = request.text
        for word in keywords:
            if word and word in enhanced:
                enhanced = enhanced.replace(word, f"【{word}】")
        return {"enhanced": enhanced}
    except Exception as e:
        return {"error": str(e)}
