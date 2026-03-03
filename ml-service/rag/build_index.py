from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Sudden voltage drop of 0.7V indicates battery degradation.",
    "Temperature spike above 35 degrees suggests thermal control failure.",
    "Gradual voltage decay over time signals power subsystem wear.",
    "Extreme temperature oscillations indicate solar panel malfunction."
]

embeddings = model.encode(documents)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

faiss.write_index(index, "rag/faiss_index.bin")

with open("rag/documents.pkl", "wb") as f:
    pickle.dump(documents, f)

print("Index built successfully.")