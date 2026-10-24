import streamlit as st

from chunker import chunk_text
from embedder import EmbeddingError, embed_documents, embed_query
from generator import NO_ANSWER, answer_question, study_from_documents
from llm_client import LLMError, generate
from loader import DocumentError, load_file
from prompts import MODES, build_prompt
from retriever import VectorStore
from validators import MAX_CHARS, validate_input

st.set_page_config(page_title="StudyBuddy", page_icon="📚", layout="wide")
st.title("📚 StudyBuddy")
st.caption("AI study tools, now with document Q&A: ask questions about your own PDFs and notes.")

# Streamlit re-runs this file on every interaction, so the index lives in session_state
if "store" not in st.session_state:
    st.session_state.store = None

# ---------------- Sidebar: documents + retrieval settings ----------------
with st.sidebar:
    st.header("Documents")
    files = st.file_uploader("PDF or TXT files", type=["pdf", "txt"], accept_multiple_files=True)

    st.header("Settings")
    chunk_size = st.slider("Chunk size (characters)", 300, 2000, 800, 100)
    overlap = st.slider("Chunk overlap", 0, 250, 100, 25)
    top_k = st.slider("Chunks to retrieve", 1, 8, 4)
    min_score = st.slider("Minimum similarity", 0.0, 1.0, 0.50, 0.05)

    process = st.button("Process documents", type="primary")

if process:
    if not files:
        st.sidebar.warning("Please upload at least one file first.")
    else:
        store = VectorStore()
        for f in files:
            try:
                text = load_file(f)
                pieces = chunk_text(text, chunk_size, overlap)
                items = [{"text": p, "source": f.name, "chunk_id": i} for i, p in enumerate(pieces)]
                bar = st.sidebar.progress(0, text=f"Embedding {f.name}...")
                vectors = embed_documents(
                    [it["text"] for it in items],
                    on_progress=lambda done, total: bar.progress(done / total, text=f"Embedding {done}/{total} chunks"),
                )
                bar.empty()
                store.add(items, vectors)
                st.sidebar.success(f"{f.name}: {len(pieces)} chunks")
            except DocumentError as e:
                st.sidebar.error(str(e))
            except EmbeddingError as e:
                st.sidebar.error(str(e))
                break
        if len(store) > 0:
            st.session_state.store = store

tab_tools, tab_docs = st.tabs(["📝 Study tools", "📄 Ask your documents"])

# ---------------- Tab 1: the original beginner app ----------------
with tab_tools:
    mode = st.radio("What do you want to do?", list(MODES.keys()), horizontal=True, key="tools_mode")
    st.info(MODES[mode]["hint"])

    user_input = st.text_area("Your content", height=250, placeholder="Paste your notes, answer or topic here...")
    st.caption(f"{len(user_input)} / {MAX_CHARS} characters")

    if st.button("Generate", type="primary", key="tools_go"):
        ok, error = validate_input(user_input)
        if not ok:
            st.warning(error)
        else:
            with st.spinner("Thinking..."):
                try:
                    output = generate(build_prompt(mode, user_input))
                except LLMError as e:
                    st.error(str(e))
                else:
                    st.success("Done!")
                    st.markdown(output)
                    with st.expander("Copy as plain text"):
                        st.code(output, language=None)

# ---------------- Tab 2: document-grounded Q&A and study modes ----------------
with tab_docs:
    store = st.session_state.store
    if store is None:
        st.info("Upload files in the sidebar and click **Process documents** to get started.")
    else:
        st.write(f"Index ready: **{len(store)} chunks** searchable.")

        doc_tasks = ["Ask a question", "Summarize notes", "Generate quiz", "Explain a concept"]
        task = st.radio("What do you want to do with your documents?", doc_tasks, horizontal=True, key="docs_mode")
        label = "Your question" if task == "Ask a question" else "Topic to focus on"
        query = st.text_input(label, placeholder="e.g. What are packet switches?")

        if st.button("Go", type="primary", key="docs_go"):
            ok, error = validate_input(query, min_chars=3)
            if not ok:
                st.warning(error)
            else:
                try:
                    with st.spinner("Searching your documents..."):
                        hits = store.search(embed_query(query), top_k, min_score)

                    if not hits:
                        st.warning(NO_ANSWER)
                        st.caption("No chunk was similar enough. Try rephrasing or lower 'Minimum similarity'.")
                    else:
                        with st.spinner("Writing..."):
                            if task == "Ask a question":
                                output = answer_question(query, hits)
                            else:
                                output = study_from_documents(task, hits)
                        st.subheader("Result")
                        st.markdown(output)

                        st.subheader("Sources used")
                        for i, h in enumerate(hits, start=1):
                            title = f"[{i}] {h['source']} (chunk {h['chunk_id']}), similarity {h['score']:.2f}"
                            with st.expander(title):
                                st.write(h["text"])
                except (EmbeddingError, LLMError) as e:
                    st.error(str(e))