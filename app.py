from fastapi import FastAPI
from pydantic import BaseModel
from models import generate_YT_summary, chatbot_with_history

app = FastAPI()

class YTRequest(BaseModel):
    ytlink: str
    session: str

class ChatRequest(BaseModel):
    user_query: str
    session: str

@app.post("/summarize")
def summarize_video(request: YTRequest):
    """Endpoint to summarize a YouTube video transcript and store it."""
    print("entered the route")
    summary =  generate_YT_summary(request.ytlink, request.session)
    print("Returning response")
    return {"summary": summary}

@app.post("/chat")
def chat_with_bot(request: ChatRequest):
    """Endpoint to interact with the chatbot using history-aware retrieval."""
    answer, history = chatbot_with_history(request.user_query, request.session)
    return {"answer": answer}



if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=8000)

