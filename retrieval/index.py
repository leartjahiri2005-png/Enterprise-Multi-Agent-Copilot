from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from ingest import load_documents, split_documents
from dotenv import load_dotenv

load_dotenv()

print("Loading docs...")
docs = load_documents()
print(f"Docs/pages: {len(docs)}")

chunks = split_documents(docs)
print(f"Chunks: {len(chunks)}")

print("Building embeddings...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

db = FAISS.from_documents(chunks, embeddings)

db.save_local("vectorstore")
print("Index built and saved.")
