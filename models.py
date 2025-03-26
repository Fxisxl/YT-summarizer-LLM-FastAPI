import os
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from vectorstore import store_chat_history, retrieve_chat_history, get_store_obj  # Import AstraDB retriever

# Load environment variables
load_dotenv()

# Set up embeddings
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize LLM (Make sure to set your Groq API key in the environment)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Please set the GROQ_API_KEY environment variable.")
llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

# Store chat histories
session_store = {}

def get_session_history(session: str) -> BaseChatMessageHistory:
    if session not in session_store:
        session_store[session] = ChatMessageHistory()
    return session_store[session]

def chatbot_with_history(user_query: str, session: str):
    """Handles chatbot responses while maintaining history."""
    
    # Retrieve past chat history from vector store
    past_conversations = retrieve_chat_history(session, user_query, k=5)
    past_texts = [doc.page_content for doc in past_conversations]
    
    # Use AstraDB as the retriever instead of Chroma
    retriever = get_store_obj(session).as_retriever()
    
    # Contextualized query retrieval
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given chat history and latest user question, reformulate it into a standalone question."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    # QA system
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the question concisely using the retrieved context. If unknown, say so.\n\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt, document_variable_name="context")
    
    # RAG pipeline
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain, get_session_history,
        input_messages_key="input", history_messages_key="chat_history", output_messages_key="answer"
    )
    
    # Invoke chain
    session_history = get_session_history(session)
    response = conversational_rag_chain.invoke(
        {"input": user_query},
        config={"configurable": {"session_id": session}}
    )
    
    # Store new conversation into vector store with metadata
    new_conversation = [
        {"text": user_query, "metadata": {"role": "user"}},
        {"text": response['answer'], "metadata": {"role": "assistant"}}
    ]
    store_chat_history(session, [msg["text"] for msg in new_conversation])
    
    return response['answer'], session_history.messages


def extract_transcript_details(youtube_video_url : str):
    try:
        video_id=youtube_video_url.split("=")[1]
        
        transcript_text=YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
            
        print(transcript)
        return transcript

    except Exception as e:
        raise e

def generate_YT_summary(ytlink: str, session: str):
    """Generates a summary from a YouTube transcript and stores it in the vector database."""
    transcript = extract_transcript_details(ytlink)
    if not transcript:
        return "No transcript available."
    
    
    prompt = ("You are a YouTube video summarizer. Given the transcript text, summarize "
              "the entire video into key points within 250 words. Keep it concise and relevant.\n\n"
              "Transcript:\n" + transcript)
    print("Starting summarization...")
    summary = llm.invoke(prompt).content if hasattr(llm.invoke(prompt), 'content') else str(llm.invoke(prompt))
    print("Summary generated:", summary) 
    # Store summary in vector store with metadata
    summary_entry = [{"text": summary, "metadata": {"role": "assistant", "source": ytlink}}]
    store_chat_history(session, summary_entry)
    
    print("Generated Summary:", summary)
    return summary






# Test Code
# def test_chatbot():
#     session_id = "youtube_summaries"
#     test_query = "What is my current package LPA ??"
    
#     print("Running chatbot test...")
#     answer, history = chatbot_with_history(test_query, session_id)
    
#     assert answer is not None, "Chatbot did not return an answer."
#     assert len(history) > 0, "Chat history is empty."
    
#     print("Test Passed! Answer:", answer)
#     print("Chat History:", history)

# if __name__ == "__main__":
#     test_chatbot()

# if __name__ == "__main__":
#     video_link = "https://www.youtube.com/watch?v=8L5kVBays24"
#     session_id = "youtube_summaries3"
#     summary_result = generate_YT_summary(video_link, session_id)
#     if summary_result:
#         print("Summary:", summary_result)