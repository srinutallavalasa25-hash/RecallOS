
import streamlit as st
from pathlib import Path
from datetime import datetime
import json

from tools import UPLOAD_DIR, index_document, search_documents
from model import generate_answer


# =====================================
# 1. Page configuration
# =====================================

st.set_page_config(
    page_title="RecallOS",
    page_icon="🧠",
    layout="wide"
)


# =====================================
# 2. Permanent chat history
# =====================================

DATA_DIR = Path("data")
CHAT_HISTORY_FILE = DATA_DIR / "chat_history.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_chat_history():
    """Load saved chat history from a JSON file."""

    if not CHAT_HISTORY_FILE.exists():
        return []

    try:
        with CHAT_HISTORY_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            history = json.load(file)

        return history if isinstance(history, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_chat_history(history):
    """Save chat history to a JSON file."""

    with CHAT_HISTORY_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4
        )


if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()


# =====================================
# 3. Page heading
# =====================================

st.title("🧠 RecallOS")
st.caption(
    "Your private AI assistant for searching your documents."
)


# =====================================
# 4. Upload and index documents
# =====================================

st.sidebar.header("📁 Document Upload")

uploaded_files = st.sidebar.file_uploader(
    "Upload your documents",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True
)

if st.sidebar.button(
    "Index Documents",
    use_container_width=True
):
    if not uploaded_files:
        st.sidebar.warning(
            "Please upload at least one document."
        )

    else:
        for uploaded_file in uploaded_files:
            file_path = Path(UPLOAD_DIR) / uploaded_file.name

            try:
                file_path.write_bytes(
                    uploaded_file.getvalue()
                )

                with st.spinner(
                    f"Processing {uploaded_file.name}..."
                ):
                    chunks = index_document(file_path)

                st.sidebar.success(
                    f"{uploaded_file.name}: "
                    f"{chunks} sections indexed"
                )

            except Exception as error:
                st.sidebar.error(
                    f"Could not process "
                    f"{uploaded_file.name}: {error}"
                )


# =====================================
# 5. Search chat history
# =====================================

st.divider()
st.subheader("🔎 Search Chat History")

history_query = st.text_input(
    "Search previous questions and answers",
    placeholder="Try a keyword such as Python or AI..."
)

history = st.session_state.chat_history

if history_query.strip():
    query = history_query.strip().casefold()

    matching_messages = [
        (index, message)
        for index, message in enumerate(history)
        if query in message.get("content", "").casefold()
    ]

    if matching_messages:
        st.caption(
            f"Found {len(matching_messages)} matching messages."
        )

        for index, message in matching_messages:
            label = (
                "Your question"
                if message.get("role") == "user"
                else "RecallOS answer"
            )

            with st.expander(
                f"{label} — Match {index + 1}"
            ):
                st.write(message.get("content", ""))

    else:
        st.info(
            "No matching messages found. "
            "Try another keyword."
        )

else:
    st.caption(
        f"{len(history)} saved messages in your chat history."
    )


# =====================================
# 6. Display chat history
# =====================================

st.divider()
st.subheader("💬 Chat History")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# =====================================
# 7. Clear chat history
# =====================================

if st.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    save_chat_history([])

    for key in [
        "latest_question",
        "latest_answer",
        "latest_sources"
    ]:
        st.session_state.pop(key, None)

    st.success("Chat history cleared.")
    st.rerun()


# =====================================
# 8. Ask your documents
# =====================================

st.divider()
st.subheader("💬 Ask your documents")

question = st.text_input(
    "Your question",
    placeholder="What are the main points in my documents?"
)

if st.button("Ask RecallOS", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("Searching your documents..."):
                matches = search_documents(question)

            if not matches:
                st.info(
                    "No indexed documents found. "
                    "Upload and index a document first."
                )

            else:
                context_parts = []

                for i, match in enumerate(matches, start=1):
                    context_parts.append(
                        f"[{i}] Source: {match['source']}\n"
                        f"Section: "
                        f"{match.get('chunk_number', 0) + 1}\n"
                        f"{match['text']}"
                    )

                context = "\n\n".join(context_parts)

                with st.spinner(
                    "Gemma is preparing your answer..."
                ):
                    answer = generate_answer(
                        question,
                        context
                    )

                # Save the latest answer for downloading.
                st.session_state.latest_question = question
                st.session_state.latest_answer = answer
                st.session_state.latest_sources = matches

                # Add question and answer to permanent history.
                st.session_state.chat_history.extend([
                    {
                        "role": "user",
                        "content": question
                    },
                    {
                        "role": "assistant",
                        "content": answer
                    }
                ])

                try:
                    save_chat_history(
                        st.session_state.chat_history
                    )
                except OSError as error:
                    st.error(
                        f"Could not save chat history: {error}"
                    )

                st.markdown("### 🧠 Answer")
                st.write(answer)

                # Show supporting document passages.
                with st.expander("📚 View source passages"):
                    for i, match in enumerate(matches, start=1):
                        st.markdown(f"### Source {i}")
                        st.write(f"**File:** {match['source']}")
                        st.write(
                            f"**Section:** "
                            f"{match.get('chunk_number', 0) + 1}"
                        )
                        st.write("**Relevant text:**")
                        st.write(match["text"])
                        st.divider()

                st.rerun()

        except Exception as error:
            st.error(
                f"Something went wrong: {error}"
            )


# =====================================
# 9. Download the latest answer
# =====================================

if st.session_state.get("latest_answer"):
    st.divider()
    st.subheader("📥 Save your answer")

    question_text = st.session_state.latest_question
    answer_text = st.session_state.latest_answer
    source_matches = st.session_state.latest_sources

    download_content = (
        "RecallOS - AI Document Answer\n"
        "================================\n\n"
        f"Question:\n{question_text}\n\n"
        f"Answer:\n{answer_text}\n\n"
        "Source passages:\n"
    )

    for i, match in enumerate(source_matches, start=1):
        download_content += (
            f"\n[{i}] File: {match['source']}\n"
            f"Section: "
            f"{match.get('chunk_number', 0) + 1}\n"
            f"{match['text']}\n"
        )

    filename = (
        "recallos_answer_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    st.download_button(
        label="⬇️ Download Answer as Text",
        data=download_content,
        file_name=filename,
        mime="text/plain"
    )


# =====================================
# 10. Footer
# =====================================

st.divider()
st.caption("RecallOS • Local AI document assistant")
