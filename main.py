from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# 데이터 규격 정의
class TextRequest(BaseModel):
    text: str
    intensity: int = 5  # 1~10 사이의 강조 농도

class StyleItem(BaseModel):
    text: str
    start: int
    end: int
    type: str

class TextResponse(BaseModel):
    original_text: str
    styles: List[StyleItem]

# 핵심 분석 API
@app.post("/api/v1/analyze")
async def analyze_text(request: TextRequest):
    # 실제 환경에서는 여기서 AI 모델을 호출하여 분석합니다.
    # 현재는 테스트를 위해 예시 데이터를 반환하도록 설정되어 있습니다.
    
    mock_data = {
        "styles": [
            {"text": "배달 수수료", "start": 6, "end": 12, "type": "bold"},
            {"text": "높습니다!", "start": 14, "end": 20, "type": "bold"},
            {"text": "500원", "start": 32, "end": 37, "type": "highlight_underline"}
        ]
    }
    
    return {
        "original_text": request.text,
        "styles": mock_data["styles"]
    }

# 서버 상태 확인용
@app.get("/")
def health_check():
    return {"status": "PH Focus Engine is running!"}
