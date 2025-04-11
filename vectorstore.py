
from langchain_astradb import AstraDBVectorStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import os

# Load environment variables
os.environ["ASTRA_DB_API_ENDPOINT"] = "https://d7ebc6da-eddd-4e14-a981-2714ea8bd0fe-us-east1.apps.astra.datastax.com"
os.environ["ASTRA_DB_APPLICATION_TOKEN"] = "AstraCS:SsrlGmfLLzjYUAZKilOjYcpd:51c8fbeb2329ac64f7ec55b5dc1f57d8294138befca21fa41ad8324ae19a4eb7"

# Configure embedding model
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_store_obj(chat_session):
    """Returns AstraDB vector store object for a given chat session."""
    return AstraDBVectorStore(
        collection_name=chat_session,
        embedding=embedding,
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    )

def store_chat_history(chat_session, conversation):
    """Stores unique chat history into AstraDB vector store with correct roles."""
    vstore = get_store_obj(chat_session)
    
    # Retrieve stored history
    existing_texts = {doc.page_content for doc in vstore.similarity_search("", k=100)}  # Using a set for fast lookup
    
    new_messages = []
    for i, msg in enumerate(conversation):
        if isinstance(msg, str):  # Convert string messages to user queries
            role = "user" if i % 2 == 0 else "assistant"  # Alternating roles based on order
            msg_dict = {"text": msg, "metadata": {"role": role}}
        elif isinstance(msg, dict) and "text" in msg:  # Ensure 'text' key exists
            msg_dict = {
                "text": msg["text"],
                "metadata": msg.get("metadata", {"role": "assistant"})  # Default to assistant if role missing
            }
        else:
            print(f"Skipping invalid message format: {msg}")
            continue  # Skip invalid messages
        
        if msg_dict["text"] not in existing_texts:  # Avoid duplicates
            new_messages.append(msg_dict)

    if new_messages:
        vstore.add_texts([msg["text"] for msg in new_messages], metadatas=[msg["metadata"] for msg in new_messages])
        print(f"Added {len(new_messages)} new messages to the vector store.")
    else:
        print("No new messages to add.")

def retrieve_chat_history(chat_session, query, k=5):
    """Retrieves the most relevant past conversations from AstraDB."""
    vstore = get_store_obj(chat_session)
    return vstore.similarity_search(query, k=k)


# Example usage
if __name__ == "__main__":
    session_id = "test_session"
    conversation_history = [
        "Hello, how are you?",
        {"text": "I'm good, thanks for asking!", "metadata": {"role": "assistant"}},
        "Tell me about LangChain.",
        {"text": "LangChain is an AI framework for building LLM applications.", "metadata": {"role": "assistant"}}
    ]
    
    store_chat_history(session_id, conversation_history)
    results = retrieve_chat_history(session_id, "What is LangChain?")
    
    for res in results:
        print(f"Retrieved ({res.metadata['role']}):", res.page_content)
