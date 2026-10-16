

import requests

OLLAMA_MODEL = "gemma3:4b"
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_answer(question, context):
    prompt = f"""
You are RecallOS, a helpful AI assistant.
Answer the question using the provided document context.
If the context does not contain the answer, say so.
Do not invent information.
Include source numbers such as [1] when they are provided in the context.

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()["response"]

    except requests.exceptions.ConnectionError:
        return (
            "Cannot connect to Ollama. "
            "Make sure Ollama is installed and running."
        )

    except requests.exceptions.Timeout:
        return "Gemma took too long to respond. Please try again."

    except requests.exceptions.RequestException as error:
        return f"Ollama request failed: {error}"
