
import chromadb
from langchain_llm7 import ChatLLM7
from langchain_core.messages import HumanMessage

# Initialize LLM7 streaming model
llm = ChatLLM7(streaming=True)

def get_chroma_client():
    """Initialize and return a ChromaDB client."""
    return chromadb.HttpClient(host="localhost", port=8000)

def retrieve_relevant_chunks(client, asset_id: str, query: str, top_k: int):
    coll = client.get_collection(name='documents')
    res = coll.query(
        query_texts=[query],
        n_results=top_k,
        where={"asset_id": asset_id},
        include=['metadatas']
    )
    raw = res.get('metadatas', [])
    if not raw or not isinstance(raw, list):
        return []
    metas = raw[0] if isinstance(raw[0], list) else raw
    return [m.get('text','') for m in metas if isinstance(m, dict)]

def stream_chat_llm7(question: str, context_chunks: list):
    prompt = (
        "You are an expert assistant. Use the context below to answer precisely.\n\n"
        "Context:\n" + "\n\n".join(context_chunks) +
        "\n\nQuestion: " + question + "\nAnswer:"
    )

    for chunk in llm.stream([HumanMessage(content=prompt)]):
        if chunk.content:
            # print("chunk.content: ",chunk.content)
            yield chunk.content