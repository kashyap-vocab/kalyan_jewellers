import os
import pickle
import faiss

    
EMBEDDING_PATH = "kalyan_index.faiss"
CHUNKS_PATH = "kalyan_chunks.pkl"

def load_saved_guidelines():
    if not os.path.exists(EMBEDDING_PATH) or not os.path.exists(CHUNKS_PATH):
        print("Error: Saved guidelines data not found. Please run preprocessing.")
        return None, None

    index = faiss.read_index(EMBEDDING_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def get_guidelines_context():
    index, chunks = load_saved_guidelines()
    if chunks:
        all_texts = [chunk.page_content for chunk in chunks]
        context = "\n\n".join(all_texts)
        if not context.strip():
            return "No specific guidelines were loaded. Please act professionally."
        return context
    return "No guidelines loaded. Please check the saved files."