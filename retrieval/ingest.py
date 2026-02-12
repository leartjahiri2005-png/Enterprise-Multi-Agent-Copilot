from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from collections import defaultdict

DOCS_PATH = Path("data/Docs")

def load_documents():
    documents = []
    for pdf in DOCS_PATH.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf))
        pages = loader.load()

        for i, page in enumerate(pages):
            page.metadata["source"] = pdf.name
            page.metadata["page"] = i + 1 

        documents.extend(pages)

    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    counters = defaultdict(int)
    for c in chunks:
        src = c.metadata.get("source", "unknown")
        c.metadata["chunk_id"] = counters[src]
        counters[src] += 1

    return chunks
