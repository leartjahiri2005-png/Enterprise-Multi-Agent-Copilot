from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

db = FAISS.load_local(
    "vectorstore",
    OpenAIEmbeddings(model="text-embedding-3-small"),
    allow_dangerous_deserialization=True
)

def search_docs(query, k=5):
    results = db.similarity_search(query, k=k, fetch_k=40, lambda_mult=0.5)
    formatted = []

    for r in results:
        formatted.append({
            "text": r.page_content,
            "source": r.metadata.get("source", "unknown"),
            "page": r.metadata.get("page", "?"),
            "chunk_id": r.metadata.get("chunk_id", "?"),
        })

    return formatted

if __name__ == "__main__":
    q = input("Ask: ")
    out = search_docs(q, k=5)

    for i, item in enumerate(out, 1):
        print(f"\n--- Result {i} ---")
        print(item["text"][:300])
        print(f'[Source: {item["source"]} | Page: {item["page"]} | Chunk: {item["chunk_id"]}]')
