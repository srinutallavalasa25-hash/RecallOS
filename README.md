
# RecallOS

RecallOS is a local AI-powered document memory and search assistant. It helps users search their documents and ask questions about their content using retrieval-augmented generation (RAG).

## Features

- Upload PDF, DOCX, TXT, and Markdown documents.
- Extract and split document text into searchable chunks.
- Create vector embeddings and store them in ChromaDB.
- Ask questions about indexed documents using a local Ollama model.
- Retrieve relevant passages to support answers.
- Display source passages used to generate answers.
- Save and search previous chat history.
- Download answers as text.
- Keep local documents and application data on your computer.

## Technology Stack

- Python
- Streamlit
- Ollama
- Gemma 3 (4B)
- ChromaDB
- Sentence Transformers
- Retrieval-Augmented Generation (RAG)

## Requirements

- Python 3.10 or a compatible version supported by your dependencies
- Ollama installed and running
- The `gemma3:4b` model downloaded in Ollama

## Installation

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Create and activate a virtual environment if desired.
4. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Download the Ollama model:

   ```bash
   ollama pull gemma3:4b
   ```

6. Make sure Ollama is running.
7. Start the application:

   ```bash
   streamlit run main.py
   ```

8. Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Privacy

RecallOS is designed for local document processing and local model inference. Documents, chat history, and the local vector database are excluded from Git using `.gitignore`.

Review your configuration and dependencies before using sensitive documents. Do not commit private documents, chat history, credentials, or other sensitive information.

## Project Files

- `main.py` — Streamlit application and chat interface.
- `model.py` — Ollama model integration.
- `tools.py` — Document extraction, chunking, indexing, and retrieval.
- `requirements.txt` — Python dependencies.
- `skill.md` — Optional project and AI-assistant instructions.
- `.gitignore` — Excludes local data and generated files from Git.

## Project Status

This project is under development. Features and setup requirements may change.

## License

No license has been specified yet. Contact the project owner before reusing or redistributing this project.
