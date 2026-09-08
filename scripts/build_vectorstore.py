import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "gita_documents.json"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

INDEX_PATH = VECTORSTORE_DIR / "gita.index"
METADATA_PATH = VECTORSTORE_DIR / "metadata.json"


# --------------------------------------------------
# 2. LOAD GITA DOCUMENTS
# --------------------------------------------------

print("Loading Bhagavad Gita documents...")

with open(DATA_PATH, "r", encoding="utf-8") as file:
    documents = json.load(file)

print(f"Loaded {len(documents)} documents.")


# --------------------------------------------------
# 3. LOAD EMBEDDING MODEL
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# --------------------------------------------------
# 4. PREPARE TEXT
# --------------------------------------------------

texts = []

for doc in documents:

    text = f"""
Chapter {doc['chapter']}: {doc['chapter_title']}

Verse: {doc['verse']}

Speaker: {doc['speaker']}

{doc['text']}
"""

    texts.append(text.strip())


# --------------------------------------------------
# 5. CREATE EMBEDDINGS
# --------------------------------------------------

print("\nCreating embeddings...")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True
)

print(f"Embedding shape: {embeddings.shape}")


# --------------------------------------------------
# 6. NORMALIZE EMBEDDINGS
# --------------------------------------------------

faiss.normalize_L2(embeddings)


# --------------------------------------------------
# 7. CREATE FAISS INDEX
# --------------------------------------------------

dimension = embeddings.shape[1]

print(f"\nVector dimension: {dimension}")

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print(f"Vectors stored in FAISS: {index.ntotal}")


# --------------------------------------------------
# 8. CREATE VECTORSTORE DIRECTORY
# --------------------------------------------------

VECTORSTORE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# 9. SAVE FAISS INDEX
# --------------------------------------------------

faiss.write_index(
    index,
    str(INDEX_PATH)
)

print(f"\nFAISS index saved to:")
print(INDEX_PATH)


# --------------------------------------------------
# 10. SAVE METADATA
# --------------------------------------------------

with open(METADATA_PATH, "w", encoding="utf-8") as file:

    json.dump(
        documents,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"Metadata saved to:")
print(METADATA_PATH)


print("\n======================================")
print("VECTOR STORE BUILD COMPLETE")
print("======================================")