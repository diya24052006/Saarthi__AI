from pathlib import Path
import re
import json
from collections import Counter


INPUT_PATH = "data/raw_gita.txt"
OUTPUT_PATH = "data/gita_documents.json"


# ============================================================
# CHAPTER INFORMATION
# Taken from the Contents of the uploaded Bhagavad Gita PDF
# ============================================================

CHAPTERS = {
    1: "The Yoga of the Despondency of Arjuna",
    2: "Sankhya Yoga",
    3: "The Yoga of Action",
    4: "The Yoga of Wisdom",
    5: "The Yoga of Renunciation of Action",
    6: "The Yoga of Meditation",
    7: "The Yoga of Wisdom and Realisation",
    8: "The Yoga of the Imperishable Brahman",
    9: "The Yoga of the Kingly Science & the Kingly Secret",
    10: "The Yoga of the Divine Glories",
    11: "The Yoga of the Vision of the Cosmic Form",
    12: "The Yoga of Devotion",
    13: "The Yoga of Distinction Between the Field & the Knower of the Field",
    14: "The Yoga of the Division of the Three Gunas",
    15: "The Yoga of the Supreme Spirit",
    16: "The Yoga of the Division Between the Divine and the Demoniacal",
    17: "The Yoga of the Division of the Threefold Faith",
    18: "The Yoga of Liberation by Renunciation",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text):
    """
    Normalize text so chapter headers can be detected
    despite differences in capitalization/spacing.
    """

    text = text.replace("\u2018", "'")
    text = text.replace("\u2019", "'")
    text = text.replace("\u201c", '"')
    text = text.replace("\u201d", '"')

    text = re.sub(r"\s+", " ", text)

    return text.strip().upper()


# ============================================================
# CHAPTER HEADER DETECTION
# ============================================================

CHAPTER_LOOKUP = {
    normalize(title): number
    for number, title in CHAPTERS.items()
}


def detect_chapter(line):
    """
    Detect a chapter heading.

    The extracted PDF repeats chapter headings on multiple pages.
    That is expected.
    """

    normalized = normalize(line)

    return CHAPTER_LOOKUP.get(normalized)


# ============================================================
# PAGE MARKERS
# ============================================================

def is_page_marker(line):
    """
    Ignore PDF page separators, page numbers,
    and repeated PDF headers.
    """

    if line.startswith("="):
        return True

    if re.fullmatch(r"PAGE\s+\d+", line, re.IGNORECASE):
        return True

    if re.fullmatch(r"\d+", line):
        return True

    # Repeated PDF header
    if normalize(line) == "BHAGAVAD GITA":
        return True

    return False


# ============================================================
# SPEAKER DETECTION
# ============================================================

SPEAKERS = {
    "ARJUNA UVAACHA:": "Arjuna",
    "ARJUNA UVAACHA": "Arjuna",
    "ARJUNA SAID:": "Arjuna",
    "ARJUNA SAID": "Arjuna",

    "SANJAYA UVAACHA:": "Sanjaya",
    "SANJAYA UVAACHA": "Sanjaya",
    "SANJAYA SAID:": "Sanjaya",
    "SANJAYA SAID": "Sanjaya",

    "SRI BHAGAAVAAN UVAACHA:": "Krishna",
    "SRI BHAGAAVAAN UVAACHA": "Krishna",
    "SRI BHAGAVAAN UVAACHA:": "Krishna",
    "SRI BHAGAVAAN UVAACHA": "Krishna",

    "SRI BHAGAVAN UVAACHA:": "Krishna",
    "SRI BHAGAVAN UVAACHA": "Krishna",

    "THE BLESSED LORD SAID:": "Krishna",
    "THE BLESSED LORD SAID": "Krishna",
}


def detect_speaker(line):
    normalized = normalize(line)

    return SPEAKERS.get(normalized)


# ============================================================
# VERSE NUMBER DETECTION
# ============================================================

VERSE_PATTERN = re.compile(
    r"^(\d+(?:-\d+)?)\.\s+(.*)"
)


def extract_verse(line):
    """
    Detect English translation lines.

    Examples:

        1. Dhritarashtra said...

        21-22. Arjuna said...

    Returns:
        (verse_number, text)

    or:
        (None, None)
    """

    match = VERSE_PATTERN.match(line)

    if not match:
        return None, None

    verse_number = match.group(1)
    verse_text = match.group(2).strip()

    return verse_number, verse_text


# ============================================================
# VERSE DOCUMENT
# ============================================================

def create_document(
    chapter,
    verse,
    speaker,
    text
):
    """
    Create one RAG document.
    """

    chapter_title = CHAPTERS.get(
        chapter,
        "Unknown Chapter"
    )

    return {
        "id": f"BG_{chapter}_{verse}",

        "chapter": chapter,

        "chapter_title": chapter_title,

        "verse": verse,

        "speaker": speaker,

        "text": text.strip(),

        "source": "Bhagavad Gita - Sri Swami Sivananda"
    }


# ============================================================
# MAIN PARSER
# ============================================================

def parse_gita():

    print("Loading raw Gita text...")

    input_file = Path(INPUT_PATH)

    if not input_file.exists():

        raise FileNotFoundError(
            f"Could not find: {INPUT_PATH}"
        )

    text = input_file.read_text(
        encoding="utf-8"
    )

    lines = text.splitlines()

    print(f"Total lines: {len(lines)}")

    documents = []

    current_chapter = None
    current_speaker = None

    current_verse = None
    current_verse_text = []

    # Indicates that we are inside the actual Gita
    gita_started = False

    detected_chapters = set()

    # --------------------------------------------------------
    # Save current verse
    # --------------------------------------------------------

    def save_current_verse():

        nonlocal current_verse
        nonlocal current_verse_text

        if current_verse is None:
            return

        if current_chapter is None:
            return

        text = " ".join(current_verse_text).strip()

        if not text:
            return

        document = create_document(
            chapter=current_chapter,
            verse=current_verse,
            speaker=current_speaker,
            text=text
        )

        documents.append(document)

        current_verse = None
        current_verse_text = []

    # --------------------------------------------------------
    # Process lines
    # --------------------------------------------------------

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # Ignore page separators/numbers
        if is_page_marker(line):
            continue

        # ----------------------------------------------------
        # CHAPTER
        # ----------------------------------------------------

        detected_chapter = detect_chapter(line)

        if detected_chapter is not None:

            # Save previous verse
            save_current_verse()

            current_chapter = detected_chapter

            detected_chapters.add(
                detected_chapter
            )

            gita_started = True

            # Reset speaker when entering chapter
            current_speaker = None

            print(
                f"Detected Chapter {detected_chapter}: "
                f"{CHAPTERS[detected_chapter]}"
            )

            continue

        # Ignore everything before Chapter 1
        if not gita_started:
            continue

        # ----------------------------------------------------
        # SPEAKER
        # ----------------------------------------------------

        speaker = detect_speaker(line)

        if speaker is not None:

            current_speaker = speaker

            continue

        # ----------------------------------------------------
        # VERSE
        # ----------------------------------------------------

        verse_number, verse_text = extract_verse(line)

        if verse_number is not None:

            # Save previous verse
            save_current_verse()

            current_verse = verse_number

            current_verse_text = [
                verse_text
            ]

            continue

        # ----------------------------------------------------
        # CONTINUATION OF CURRENT VERSE
        # ----------------------------------------------------

        if current_verse is not None:

            current_verse_text.append(line)

    # Save final verse
    save_current_verse()

    return documents, detected_chapters


# ============================================================
# VALIDATION
# ============================================================

def validate_documents(documents, detected_chapters):

    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)

    print(
        f"\nTotal documents: {len(documents)}"
    )

    print(
        f"Chapters detected: "
        f"{len(detected_chapters)}/18"
    )

    missing_chapters = (
        set(CHAPTERS.keys())
        - detected_chapters
    )

    if missing_chapters:

        print(
            "\nWARNING: Missing chapters:"
        )

        for chapter in sorted(missing_chapters):

            print(
                f"  Chapter {chapter}: "
                f"{CHAPTERS[chapter]}"
            )

    else:

        print(
            "\nAll 18 chapters detected successfully!"
        )

    # --------------------------------------------------------
    # Chapter distribution
    # --------------------------------------------------------

    chapter_counts = Counter(
        document["chapter"]
        for document in documents
    )

    print("\nChapter distribution:")

    for chapter in range(1, 19):

        count = chapter_counts.get(
            chapter,
            0
        )

        print(
            f"Chapter {chapter:2d}: {count} documents"
        )

    # --------------------------------------------------------
    # Missing metadata
    # --------------------------------------------------------

    missing_chapter = sum(
        1
        for d in documents
        if d["chapter"] is None
    )

    missing_verse = sum(
        1
        for d in documents
        if not d["verse"]
    )

    missing_text = sum(
        1
        for d in documents
        if not d["text"]
    )

    print("\nMetadata validation:")

    print(
        f"Missing chapter: {missing_chapter}"
    )

    print(
        f"Missing verse:   {missing_verse}"
    )

    print(
        f"Missing text:    {missing_text}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    documents, detected_chapters = parse_gita()

    validate_documents(
        documents,
        detected_chapters
    )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    output_file = Path(OUTPUT_PATH)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file.write_text(
        json.dumps(
            documents,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )

    # --------------------------------------------------------
    # Show sample documents
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("SAMPLE DOCUMENTS")
    print("=" * 60)

    for document in documents[:3]:

        print(
            json.dumps(
                document,
                indent=2,
                ensure_ascii=False
            )
        )
