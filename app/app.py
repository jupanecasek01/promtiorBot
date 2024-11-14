from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot import execute_agent  # Suponiendo que tienes un archivo bot.py con tu lógica
import uvicorn

app = FastAPI()

# Ruta raíz
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Promtior Bot API!"}

# Definir el esquema de entrada para la pregunta y el ID de la conversación
class QuestionRequest(BaseModel):
    question: str
    conversation_id: str = ""

# Ruta para recibir preguntas
@app.post("/ask")
async def ask(data: QuestionRequest):
    question = data.question
    conversation_id = data.conversation_id
    
    # Llama a la función de tu bot para obtener la respuesta
    response = execute_agent(question, conversation_id)
    
    # Asegúrate de devolver la respuesta que tiene la clave 'final_response'
    return {"response": response["final_response"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)