from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.bot import execute_agent, initialize_cache_variables
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_cache_variables()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Promtior Bot API!"}


class QuestionRequest(BaseModel):
    question: str
    conversation_id: str = ""


@app.post("/")
async def ask(data: QuestionRequest):
    question = data.question
    conversation_id = data.conversation_id
  
    try:
        response = execute_agent(question, conversation_id)
   
        if "final_response" not in response:
            raise ValueError("La respuesta no contiene 'final_response'")
        
        return {"response": response["final_response"]}
    
    except Exception as e:
       
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
