import faiss
import pickle
import numpy as np

from backend.embedder import embed_texts

INDEX_PATH = "data/faiss_index.bin"
META_PATH = "data/job_metadata.pkl"


def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata


def retrieve_jobs(query: str, top_k: int = 5):
    """
    Retrieve top_k relevant jobs for a given query string.
    """
    index, metadata = load_index()

    query_embedding = embed_texts([query])
    query_vector = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []
    for idx in indices[0]:
        results.append(metadata[idx])

    return results


if __name__ == "__main__":
    test_query = "Python Machine Learning AI Intern"
    jobs = retrieve_jobs(test_query)

    print("🔍 Retrieved Jobs:")
    for job in jobs:
        print(f"- {job['company']} | {job['role']} | {job['location']}")
