from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# 1. 메인 주소('/')로 접속했을 때 보여줄 화면입니다.
@app.get("/")
def read_root():
    return {"message": "PH Focus Engine이 정상 작동 중입니다!"}

# 2. 기존 기능(/process)은 그대로 유지합니다.
@app.post("/process")
def process_text(request: dict):
    return {"result": "성공적으로 요청을 받았습니다."}
