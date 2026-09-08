import json
import os
import re
from pathlib import Path
from threading import Lock

# Limit CPU thread usage.
# This can reduce unnecessary memory usage on small deployment instances.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import faiss
from sentence_transformers import SentenceTransformer


# ============================================================
# BASE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "vectorstore" / "gita.index"
METADATA_PATH = BASE_DIR / "vectorstore" / "metadata.json"


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K = 5
MAX_TOP_K = 10
CANDIDATE_K = 15

MAX_QUERY_LENGTH = 1000


# ============================================================
# LAZY-LOADED RESOURCES
# ============================================================

_index = None
_metadata = None
_model = None

_index_lock = Lock()
_model_lock = Lock()


# ============================================================
# QUERY CLEANING
# ============================================================

def clean_query(query: str) -> str:
    """
    Clean and normalize the user's search query.
    """

    if not query:
        return ""

    query = str(query)

    # Convert to lowercase
    query = query.lower()

    # Remove special characters
    query = re.sub(r"[^\w\s]", " ", query)

    # Remove extra whitespace
    query = re.sub(r"\s+", " ", query)

    query = query.strip()

    # Prevent unnecessarily large embedding input
    query = query[:MAX_QUERY_LENGTH]

    return query


# ============================================================
# LOAD FAISS INDEX
# ============================================================

def get_index():
    """
    Load the FAISS index only when search is actually needed.

    This prevents FAISS from consuming memory during
    FastAPI startup.
    """

    global _index

    if _index is None:

        with _index_lock:

            if _index is None:

                print("Loading FAISS index...")

                if not INDEX_PATH.exists():
                    raise FileNotFoundError(
                        f"FAISS index not found: {INDEX_PATH}"
                    )

                _index = faiss.read_index(
                    str(INDEX_PATH)
                )

                print(
                    f"FAISS index loaded: {_index.ntotal} vectors"
                )

    return _index


# ============================================================
# LOAD METADATA
# ============================================================

def get_metadata():
    """
    Load Gita metadata only when required.
    """

    global _metadata

    if _metadata is None:

        print("Loading Gita metadata...")

        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {METADATA_PATH}"
            )

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            _metadata = json.load(file)

        print(
            f"Gita metadata loaded: {len(_metadata)} documents"
        )

    return _metadata


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

def get_model():
    """
    Load the Sentence Transformer model lazily.

    The model is loaded only on the first search request
    and reused afterwards.
    """

    global _model

    if _model is None:

        with _model_lock:

            if _model is None:

                print(
                    "Loading embedding model..."
                )

                _model = SentenceTransformer(
                    MODEL_NAME,
                    device="cpu"
                )

                _model.eval()

                print(
                    "Embedding model ready!"
                )

    return _model


# ============================================================
# SEMANTIC SEARCH
# ============================================================

def search_gita(
    query: str,
    top_k: int = DEFAULT_TOP_K
):
    """
    Perform semantic search over Bhagavad Gita passages.

    Parameters
    ----------
    query:
        Semantic search query.

    top_k:
        Number of Gita passages to return.

    Returns
    -------
    list:
        Ranked Gita passages.
    """

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    if not query:
        return []

    cleaned_query = clean_query(query)

    if not cleaned_query:
        return []

    # --------------------------------------------------------
    # Validate top_k
    # --------------------------------------------------------

    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = DEFAULT_TOP_K

    top_k = max(
        1,
        min(top_k, MAX_TOP_K)
    )

    # --------------------------------------------------------
    # Load resources only when needed
    # --------------------------------------------------------

    index = get_index()
    metadata = get_metadata()
    model = get_model()

    if index.ntotal == 0:
        return []

    # --------------------------------------------------------
    # Generate embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        [cleaned_query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    # --------------------------------------------------------
    # Search FAISS
    # --------------------------------------------------------

    candidate_k = min(
        max(CANDIDATE_K, top_k),
        index.ntotal
    )

    scores, indices = index.search(
        query_embedding,
        candidate_k
    )

    # --------------------------------------------------------
    # Build result list
    # --------------------------------------------------------

    results = []

    seen_ids = set()

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        # Invalid index
        if idx < 0:
            continue

        # Metadata safety check
        if idx >= len(metadata):
            continue

        document = metadata[idx]

        document_id = document.get(
            "id",
            f"index_{idx}"
        )

        # Prevent duplicate documents
        if document_id in seen_ids:
            continue

        seen_ids.add(document_id)

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

        if len(results) >= top_k:
            break

    return results


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(results):
    """
    Display search results in the terminal.
    """

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
            f"Chapter {result.get('chapter')} "
            f"| Verse {result.get('verse')}"
        )

        print(
            f"Score: "
            f"{result.get('score', 0):.4f}"
        )

        print(
            f"Speaker: "
            f"{result.get('speaker')}"
        )

        print(
            f"Title: "
            f"{result.get('chapter_title')}"
        )

        print(
            f"\n{result.get('text')}"
        )

        print("-" * 70)


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("🌱 AI SAARTHI - GITA SEMANTIC SEARCH")
    print("=" * 70)

    print(
        "\nFAISS, metadata and embedding model "
        "will load only when the first search is performed."
    )

    while True:

        query = input(
            "\nEnter your situation "
            "(or 'exit'):\n> "
        ).strip()

        if query.lower() == "exit":

            print(
                "\nGoodbye 🌱"
            )

            break

        if not query:

            print(
                "Please enter a search query."
            )

            continue

        try:

            results = search_gita(
                query,
                top_k=5
            )

            display_results(results)

        except Exception as e:

            print(
                "\n❌ SEARCH ERROR"
            )

            print(
                "-" * 70
            )

            print(
                str(e)
            )