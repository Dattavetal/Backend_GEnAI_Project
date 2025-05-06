from typing import TypedDict
from langgraph.graph import StateGraph, END
from config import Config
from utils import get_chroma_client, retrieve_relevant_chunks
from langchain_llm7 import ChatLLM7
from langchain_core.messages import HumanMessage

# Initialize LLM
llm = ChatLLM7()

# Define the schema for state passing between nodes
class RAGState(TypedDict):
    asset_id: str
    query: str
    chunks: list[str]
    prompt: str
    response: str
    final_response: str

# Build the graph
def build_rag_graph():
    graph = StateGraph(RAGState)

    def retrieve_node(state: RAGState):
        chunks = retrieve_relevant_chunks(
            get_chroma_client(Config.CHROMA_API_URL),
            state["asset_id"], state["query"], Config.TOP_K
        )
        return {"chunks": chunks}

    def build_prompt_node(state: RAGState):
        prompt = (
            "You are an expert assistant. Use the context below to answer the question precisely.\n\n"
            "Context:\n" + "\n\n".join(state["chunks"]) +
            "\n\nQuestion: " + state["query"] + "\nAnswer:"
        )
        return {"prompt": prompt}

    def generate_node(state: RAGState):
        output = llm.invoke([HumanMessage(content=state["prompt"])])
        return {"response": output.content}

    def final_node(state: RAGState):
        return {"final_response": state["response"]}

    # Register nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("build_prompt", build_prompt_node)
    graph.add_node("generate", generate_node)
    graph.add_node("final", final_node)

    # Wire the edges
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "build_prompt")
    graph.add_edge("build_prompt", "generate")
    graph.add_edge("generate", "final")
    graph.add_edge("final", END)

    return graph.compile()

if __name__ == "__main__":
    asset_id = input("Enter Asset ID: ").strip()
    query = input("Enter your query: ").strip()

    rag_graph = build_rag_graph()
    result = rag_graph.invoke({
        "asset_id": asset_id,
        "query": query
    })

    print("\nRAG Answer:", result["final_response"])

