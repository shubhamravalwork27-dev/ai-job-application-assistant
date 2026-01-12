import faiss
import pandas as pd
import os
import pickle
import numpy as np

from backend.embedder import embed_texts

INDEX_PATH = "data/faiss_index.bin"
META_PATH = "data/job_metadata.pkl"

def build_faiss_index(csv_path: str):
    print("🔹 Loading jobs CSV...")
    df = pd.read_csv(csv_path)

    print(f"🔹 Loaded {len(df)} jobs")

    texts = (
        df["role"] + " " +
        df["skills"] + " " +
        df["description"]
    ).tolist()

    print("🔹 Generating embeddings...")
    embeddings = embed_texts(texts)

    dimension = len(embeddings[0])
    print(f"🔹 Embedding dimension: {dimension}")

    index = faiss.IndexFlatL2(dimension)

    # ✅ CORRECT FAISS ADD
    index.add(np.array(embeddings).astype("float32"))

    os.makedirs("data", exist_ok=True)

    print("🔹 Saving FAISS index...")
    faiss.write_index(index, INDEX_PATH)

    print("🔹 Saving metadata...")
    metadata = df.to_dict(orient="records")
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("✅ FAISS index built and saved successfully.")


if __name__ == "__main__":
    print("🚀 Starting FAISS index builder...")
    build_faiss_index("data/jobs.csv")
