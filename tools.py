

from pathlib import Path
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document


# =====================================
# 1. Project directories
# =====================================

DATA_DIR = Path("data")
UPLOAD_DIR = DATA_DIR / "uploads"
DB_DIR = DATA_DIR / "chroma_db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)


# =====================================
# 2. Load the embedding model
# =====================================

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# =====================================
# 3. Connect to ChromaDB
# =====================================

client = chromadb.PersistentClient(
    path=str(DB_DIR)
)

collection = client.get_or_create_collection(
    name="recallos_documents"
)


# =====================================
# 4. Extract document text
# =====================================

def extract_text(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(path))

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif suffix == ".docx":
        document = Document(str(path))

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    elif suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")

    else:
        raise ValueError(
            "Supported formats: PDF, DOCX, TXT, MD"
        )


# =====================================
# 5. Split text into sections
# =====================================

def split_text(text, chunk_size=700, overlap=100):
    words = text.split()
    chunks = []

    step = max(1, chunk_size - overlap)

    for start in range(0, len(words), step):
        chunk = " ".join(
            words[start:start + chunk_size]
        )

        if chunk:
            chunks.append(chunk)

    return chunks


# =====================================
# 6. Create a document ID
# =====================================

def get_document_id(file_path):
    path = Path(file_path)

    return hashlib.sha256(
        path.name.encode("utf-8")
    ).hexdigest()[:20]


# =====================================
# 7. Index a document
# =====================================

def index_document(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    text = extract_text(path)

    if not text.strip():
        raise ValueError(
            "No readable text found in this document."
        )

    chunks = split_text(text)

    if not chunks:
        raise ValueError(
            "No text sections could be created."
        )

    document_id = get_document_id(path)

    # Replace the old indexed sections for this file.
    collection.delete(
        where={"document_id": document_id}
    )

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    ids = [
        f"{document_id}_{i}"
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {
                "source": path.name,
                "document_id": document_id,
                "chunk_number": i
            }
            for i in range(len(chunks))
        ]
    )

    return len(chunks)


# =====================================
# 8. List indexed documents
# =====================================

def list_indexed_documents():
    """Return one entry per indexed document."""

    result = collection.get(
        include=["metadatas"]
    )

    documents = {}

    metadatas = result.get("metadatas") or []

    for metadata in metadatas:
        if not metadata:
            continue

        document_id = metadata.get("document_id")
        source = metadata.get("source", "Unknown document")

        if not document_id:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "source": source,
                "sections": 0
            }

        documents[document_id]["sections"] += 1

    return sorted(
        documents.values(),
        key=lambda item: item["source"].casefold()
    )


# =====================================
# 9. Remove a document from the index
# =====================================

def delete_indexed_document(document_id):
    """Remove a document's sections from ChromaDB."""

    if not document_id:
        raise ValueError("Document ID is required.")

    collection.delete(
        where={"document_id": document_id}
    )


# =====================================
# 10. Search indexed documents
# =====================================

def search_documents(question, top_k=4):
    question = question.strip()

    if not question:
        return []

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_embedding = embedding_model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total_chunks),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    matches = []

    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        matches.append({
            "text": document,
            "source": metadata.get(
                "source", "Unknown document"
            ),
            "chunk_number": metadata.get(
                "chunk_number", 0
            ),
            "distance": distance
        })

    return matches
