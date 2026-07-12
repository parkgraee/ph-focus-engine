from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# API 키를 환경 변수에서 가져옵니다.
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TextRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.post("/process")
def process_text(request: TextRequest):
    return {"result": "Success"}
