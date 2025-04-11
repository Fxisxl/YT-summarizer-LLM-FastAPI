
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from models import generate_YT_summary, chatbot_with_history

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (you can specify a list of allowed domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


class YTRequest(BaseModel):
    user_query: str
    session: str
    mode : str

class ChatRequest(BaseModel):
    user_query: str
    session: str
    mode : str

@app.post("/summarize")
def summarize_video(request: YTRequest):
    """Endpoint to summarize a YouTube video transcript and store it."""
    print("entered the route : " , request.mode)
    summary =  generate_YT_summary(request.user_query, request.session)
    print("Returning response")
    return {"summary": summary}

@app.post("/chat")
def chat_with_bot(request: ChatRequest):
    """Endpoint to interact with the chatbot using history-aware retrieval."""
    print("entered the CHAT route " , request.mode)
    answer ,history = chatbot_with_history(request.user_query, request.session)
    print("Returning response")
    print(answer)
    return {"answer": answer}



if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=8000)

#uvicorn app:app --host 0.0.0.0 --port 8000 --reload
