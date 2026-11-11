import os
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

RAG_DIR=Path(__file__).resolve().parent
PDF_PATH=RAG_DIR/"fundamental Analysis For Dummies.pdf"
CHROMA_DIR=str(RAG_DIR/"chrom_db")

embeddings= HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_or_load_vectorstore():
    """Builds persistent ChromaDB on first run, loads existing index otherwise"""
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        return Chroma(persist_directory=CHROMA_DIR,embedding_function=embeddings)

    if not PDF_PATH.exists():
        matched=list(RAG_DIR.glob("*.pdf"))
        if not matched:
            raise FileNotFoundError(f"PDF not found in {RAG_DIR}")
        target_pdf=matched[0]
    else:
        target_pdf=PDF_PATH

    print(f"[RAG] Indexing book: {target_pdf.name}...")
    loader=PyPDFLoader(str(target_pdf))
    docs=loader.load()

    splitter= RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150)
    chunks=splitter.split_documents(docs)

    vector_store=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    print(f"[RAG] successfully indexed {len(chunks)} chunks.")
    return vector_store

_vectorestore=None

def get_vectorestore():
    global _vectorestore
    if _vectorestore is None:
        _vectorestore=build_or_load_vectorstore()
    return _vectorestore

async def query_fundamental_risk_rules(query:str,k:int=3)->str:
    vs= get_vectorestore()
    result = vs.similarity_search(query,k=k)
    formatted_passages=[]
    for doc in result:
        page_num=doc.metadata.get("page","unknown")
        snippet=doc.page_content.replace("\n", " ").strip()
        formatted_passages.append(f"[Page {page_num}] \"{snippet[:300]}...\"")

    return "\n\n".join(formatted_passages)


