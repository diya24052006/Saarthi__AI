import json
import re
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "vectorstore" / "gita.index"
METADATA_PATH = BASE_DIR / "vectorstore" / "metadata.json"


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K = 5

# Retrieve more candidates first.
CANDIDATE_K = 10


# ============================================================
# LOAD FAISS
# ============================================================

print("Loading FAISS index...")

index = faiss.read_index(
    str(INDEX_PATH)
)

print(
    f"Vectors loaded: {index.ntotal}"
)


# ============================================================
# LOAD METADATA
# ============================================================

print("Loading metadata...")

with open(
    METADATA_PATH,
    "r",
    encoding="utf-8"
) as file:

    metadata = json.load(file)


print(
    f"Metadata loaded: {len(metadata)} documents"
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("\nLoading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Model ready!")


# ============================================================
# CLEAN QUERY
# ============================================================

def clean_query(query: str) -> str:

    query = query.lower()

    # Remove unnecessary punctuation
    query = re.sub(
        r"[^\w\s]",
        " ",
        query
    )

    # Remove excessive whitespace
    query = re.sub(
        r"\s+",
        " ",
        query
    )

    return query.strip()


# ============================================================
# SEARCH GITA
# ============================================================

def search_gita(
    query: str,
    top_k: int = DEFAULT_TOP_K
):

    if not query:

        return []


    # --------------------------------------------------------
    # Clean query
    # --------------------------------------------------------

    cleaned_query = clean_query(
        query
    )


    # --------------------------------------------------------
    # Create embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        [cleaned_query],
        normalize_embeddings=True
    )


    # --------------------------------------------------------
    # Search FAISS
    # --------------------------------------------------------

    scores, indices = index.search(
        query_embedding,
        CANDIDATE_K
    )


    results = []

    seen_ids = set()


    # --------------------------------------------------------
    # Process candidates
    # --------------------------------------------------------

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx < 0:
            continue


        if idx >= len(metadata):
            continue


        document = metadata[idx]


        # ----------------------------------------------------
        # Avoid duplicate documents
        # ----------------------------------------------------

        document_id = document.get(
            "id",
            f"index_{idx}"
        )

        if document_id in seen_ids:
            continue

        seen_ids.add(document_id)


        # ----------------------------------------------------
        # Create result
        # ----------------------------------------------------

        result = {
            "id": document_id,
            "chapter": document.get(
                "chapter"
            ),
            "chapter_title": document.get(
                "chapter_title"
            ),
            "verse": document.get(
                "verse"
            ),
            "speaker": document.get(
                "speaker"
            ),
            "text": document.get(
                "text"
            ),
            "source": document.get(
                "source"
            ),
            "score": float(score)
        }

        results.append(result)


    # --------------------------------------------------------
    # Return only requested number
    # --------------------------------------------------------

    return results[:top_k]


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    results
):

    print("\n")
    print("=" * 70)
    print("GITA SEARCH RESULTS")
    print("=" * 70)


    if not results:

        print("No results found.")

        return


    for i, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{i}. "
            f"Chapter {result['chapter']} "
            f"| Verse {result['verse']}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Speaker: {result['speaker']}"
        )

        print(
            f"Title: {result['chapter_title']}"
        )

        print(
            f"\n{result['text']}"
        )

        print("-" * 70)


# ============================================================
# TEST SEARCH
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("🌱 AI SAARTHI - GITA SEMANTIC SEARCH")
    print("=" * 70)

    while True:

        query = input(
            "\nEnter your situation (or 'exit'):\n> "
        ).strip()


        if query.lower() == "exit":

            print("\nGoodbye 🌱")

            break


        results = search_gita(
            query,
            top_k=5
        )

        display_results(
            results
        )