# rag_pipeline.py

import logging
from datetime import datetime
import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, TextGenerationPipeline
import torch
import re

# Set up logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=f"logs/chat_{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load FAISS index and documents
index = faiss.read_index("docs/lmu_index.faiss")
with open("docs/lmu_documents.pkl", "rb") as f:
    documents = pickle.load(f)

# Load embedding model (improved retrieval)
embedder = SentenceTransformer("intfloat/e5-small-v2")

# Load language model
model_name = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Create generation pipeline
qa_pipeline = TextGenerationPipeline(model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

def get_answer(query: str) -> str:
    # Encode and normalize the query for better search accuracy
    query_embedding = embedder.encode([query], normalize_embeddings=True)
    k = 5  # number of relevant chunks to retrieve
    distances, indices = index.search(np.array(query_embedding), k)

    # Extract and clean context chunks
    seen = set()
    context_parts = []
    for i in indices[0]:
        text = documents[i]["text"]
        text = text.replace("â", "'").replace("’", "'").replace("“", '"').replace("”", '"')
        sentences = re.split(r'(?<=[.!?]) +', text)
        truncated = ""
        for sentence in sentences:
            if len(truncated) + len(sentence) <= 500:
                truncated += sentence + " "
            else:
                break
        cleaned = truncated.strip()
        if cleaned not in seen:
            seen.add(cleaned)
            context_parts.append(cleaned)

    context = "\n".join(context_parts)

    # Build the prompt with safety guardrails
    prompt = f"""You are a helpful academic advisor for LMU Munich. Use ONLY the context below to answer the user's question. 
If the answer is not clearly in the context, say "I’m not sure, please refer to LMU’s official website."

Context:
{context}

Question:
{query}

Answer:"""

    # Generate the response
    response = qa_pipeline(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)
    answer = response[0]["generated_text"].split("Answer:")[-1].strip()

    # Logging
    logging.info(f"User Query: {query}")
    logging.info(f"Context Used: {context}")
    logging.info(f"Generated Answer: {answer}")

    return answer
