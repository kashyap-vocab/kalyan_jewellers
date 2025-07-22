import os
import pickle
import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# New PDF path and output paths
GUIDELINES_PDF_PATH = "Kalyan_Jewellers_SOP_Detailed.pdf"
EMBEDDING_PATH = "kalyan_index.faiss"
CHUNKS_PATH = "kalyan_chunks.pkl"

def load_and_chunk_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

def get_embeddings(texts):
    embeddings = []
    for doc in texts:
        try:
            response = genai.embed_content(
                model="models/embedding-001",
                content=doc.page_content,
                task_type="retrieval_document",
            )
            if response and "embedding" in response:
                embeddings.append(response["embedding"])
        except Exception as e:
            print(f"Embedding error: {e}")
            continue
    return embeddings

def save_index_and_chunks():
    chunks = load_and_chunk_pdf(GUIDELINES_PDF_PATH)
    embeddings = get_embeddings(chunks)

    if not embeddings:
        print("No embeddings generated. Aborting.")
        return

    embeddings_np = np.array(embeddings, dtype=np.float32)
    index = faiss.IndexFlatL2(embeddings_np.shape[1])
    index.add(embeddings_np)
    faiss.write_index(index, EMBEDDING_PATH)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Kalyan Jewellers SOP preprocessed and saved successfully.")

if __name__ == "__main__":
    save_index_and_chunks()
