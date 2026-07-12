from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TextRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "PH Focus Engine is running!"}

@app.post("/process")
def process_text(request: TextRequest):
    # 여기에 핵심 AI 분석 로직이 들어갑니다.
    # 예시: 특정 단어를 강조하는 로직
    original_text = request.text
    
    # 지금은 아주 간단한 예시로 '중요'라는 단어를 찾으면 대괄호를 씌워볼게요.
    enhanced_text = original_text.replace("중요", "【중요】")
    
    return {
        "original": original_text,
        "enhanced": enhanced_text,
        "method": "bracket_highlight"
    }
