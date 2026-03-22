import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("rag/faiss_index.bin")

# Load documents
with open("rag/documents.pkl", "rb") as f:
    documents = pickle.load(f)

# OpenAI client — requires OPENAI_API_KEY environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_explanation(anomaly_data: dict) -> str:
    """
    Generates a contextual explanation for a detected anomaly using RAG:
    1. Converts anomaly data to a text query
    2. Embeds the query using sentence-transformers
    3. Retrieves the 2 most similar fault descriptions from the FAISS index
    4. Sends the retrieved context and anomaly data to OpenAI GPT-4o-mini
    5. Returns a human-readable explanation of the likely cause and recommended action
    """

    # Convert anomaly dict to a text query
    query_text = (
        f"Satellite anomaly detected. "
        f"Temperature: {anomaly_data['temperature']}, "
        f"Voltage: {anomaly_data['voltage']}, "
        f"Temp delta: {anomaly_data['temp_delta']}, "
        f"Voltage delta: {anomaly_data['volt_delta']}."
    )

    # Embed the query
    query_vector = embed_model.encode([query_text])

    # Retrieve 2 most similar fault descriptions from FAISS index
    distances, indices = index.search(np.array(query_vector), k=2)
    retrieved_context = "\n".join([documents[i] for i in indices[0]])

    # Generate explanation via OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an aerospace systems analyst."
            },
            {
                "role": "user",
                "content": (
                    f"Current anomaly:\n{query_text}\n\n"
                    f"Similar past events:\n{retrieved_context}\n\n"
                    f"Explain the likely cause and recommended action."
                )
            }
        ]
    )

    return response.choices[0].message.content