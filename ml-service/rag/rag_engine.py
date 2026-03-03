import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("rag/faiss_index.bin")

# Load documents
with open("rag/documents.pkl", "rb") as f:
    documents = pickle.load(f)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_explanation(anomaly_data: dict):

    # Convert anomaly dict to text query
    query_text = (
        f"Satellite anomaly detected. "
        f"Temperature: {anomaly_data['temperature']}, "
        f"Voltage: {anomaly_data['voltage']}, "
        f"Temp delta: {anomaly_data['temp_delta']}, "
        f"Voltage delta: {anomaly_data['volt_delta']}."
    )

    # Embed query
    query_vector = embed_model.encode([query_text])

    # Search similar past events
    distances, indices = index.search(np.array(query_vector), k=2)

    retrieved_context = "\n".join([documents[i] for i in indices[0]])

    # Send to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an aerospace systems analyst."
            },
            {
                "role": "user",
                "content": f"""
Current anomaly:
{query_text}

Similar past events:
{retrieved_context}

Explain the likely cause and recommended action.
"""
            }
        ]
    )

    return response.choices[0].message.content