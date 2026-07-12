from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TextRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Server is running"}
