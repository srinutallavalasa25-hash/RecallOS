
# RecallOS — Project Instructions

## Purpose
RecallOS is a local AI-powered document search and question-answering assistant.

## Technology
- Python
- Streamlit
- Ollama with Gemma 3 (4B)
- ChromaDB for vector storage
- Sentence Transformers for text embeddings

## Main Files
- `main.py`: User interface, document uploads, chat history, and question-answering workflow.
- `model.py`: Communication with the local Ollama model.
- `tools.py`: Document extraction, text chunking, indexing, and retrieval.
- `requirements.txt`: Python dependencies.

## Development Guidelines
1. Keep changes beginner-friendly and easy to maintain.
2. Preserve existing functionality when changing code.
3. Do not place API keys, passwords, or other secrets in source files.
4. Do not commit private documents, chat history, or the local vector database.
5. Handle errors clearly and avoid exposing sensitive document contents in logs.
6. Test changes locally before committing them.
7. Update `README.md` when installation steps or features change.

## Privacy
Process documents locally where possible. Explain clearly if a feature sends data to an external service.

## Important
This file documents project conventions. It does not automatically control the AI model unless an application or tool explicitly loads it.
