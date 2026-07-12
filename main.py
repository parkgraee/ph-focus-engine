from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TextRequest(BaseModel):
    text: str

# 1. 여기를 추가하세요: 브라우저로 접속했을 때 보여줄 메인 화면
@app.get("/")
def read_root():
    return {"message": "PH Focus Engine이 정상 작동 중입니다!"}

# 2. 기존 /process 코드는 유지
@app.post("/process")
def process_text(request: TextRequest):
    # (기존 로직 그대로)
    return {"status": "ok"}
