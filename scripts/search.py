import json
import re
from pathlib import Path
from threading import Lock

import faiss
from sentence_transformers import SentenceTransformer


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "vectorstore" / "gita.index"
METADATA_PATH = BASE_DIR / "vectorstore" / "metadata.json"


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K = 5
CANDIDATE_K = 10

# Maximum characters sent to the embedding model.
# This prevents unnecessarily large user queries.
MAX_QUERY_LENGTH = 1000


# ============================================================
# GLOBAL RESOURCES
# ============================================================

_index = None
_metadata = None
_model = None

# Prevent multiple requests from loading the model simultaneously.
_model_lock = Lock()
_index_lock = Lock()


# ============================================================
# QUERY CLEANING
# ============================================================

def clean_query(query: str) -> str:
    """
    Clean the user's query before generating an embedding.
    """

    if not query:
        return ""

    query = str(query)

    # Convert to lowercase
    query = query.lower()

    # Remove special characters
    query = re.sub(r"[^\w\s]", " ", query)

    # Remove extra spaces
    query = re.sub(r"\s+", " ", query)

    # Remove unnecessary whitespace
    query = query.strip()

    # Limit query length
    query = query[:MAX_QUERY_LENGTH]

    return query


# ============================================================
# LOAD FAISS INDEX
# ============================================================

def get_index():
    """
    Load FAISS index only when it is actually needed.
    """

    global _index

    if _index is None:

        with _index_lock:

            # Double-check after acquiring the lock
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
            f"Metadata loaded: {len(_metadata)} documents"
        )

    return _metadata


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

def get_model():
    """
    Load Sentence Transformer only when semantic search
    is actually requested.

    The model is loaded once and then reused.
    """

    global _model

    if _model is None:

        with _model_lock:

            # Double-check after acquiring lock
            if _model is None:

                print(
                    "Loading embedding model..."
                )

                _model = SentenceTransformer(
                    MODEL_NAME,
                    device="cpu"
                )

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
    Search Bhagavad Gita passages using semantic similarity.

    Parameters
    ----------
    query : str
        User's semantic search query.

    top_k : int
        Number of results to return.

    Returns
    -------
    list
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

    top_k = max(1, min(top_k, 20))

    # --------------------------------------------------------
    # Load resources lazily
    # --------------------------------------------------------

    index = get_index()
    metadata = get_metadata()
    model = get_model()

    # --------------------------------------------------------
    # Generate query embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        [cleaned_query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    # --------------------------------------------------------
    # FAISS search
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
    # Build results
    # --------------------------------------------------------

    results = []

    seen_ids = set()

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        # Invalid FAISS index
        if idx < 0:
            continue

        # Safety check
        if idx >= len(metadata):
            continue

        document = metadata[idx]

        document_id = document.get(
            "id",
            f"index_{idx}"
        )

        # Avoid duplicate documents
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
    Pretty-print search results in the terminal.
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
# TERMINAL TESTING
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("🌱 AI SAARTHI - GITA SEMANTIC SEARCH")
    print("=" * 70)

    print(
        "\nResources will be loaded only when "
        "the first search is performed."
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

        results = search_gita(
            query,
            top_k=5
        )

        display_results(results)