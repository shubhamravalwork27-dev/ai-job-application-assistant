from sentence_transformers import SentenceTransformer

# Load embedding model once
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of texts into embeddings.
    """
    embeddings = _model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()
