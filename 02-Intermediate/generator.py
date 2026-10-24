from llm_client import generate
from prompts import build_prompt, build_rag_prompt

NO_ANSWER = "I couldn't find that in the uploaded documents."


def _numbered_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{i}] (from {c['source']})\n{c['text']}" for i, c in enumerate(chunks, start=1))


def answer_question(question: str, chunks: list[dict]) -> str:
    """Grounded Q&A: answer only from the retrieved chunks."""
    return generate(build_rag_prompt(question, _numbered_context(chunks), NO_ANSWER))


def study_from_documents(mode: str, chunks: list[dict]) -> str:
    """Run a beginner mode (summary, quiz, explain) on the retrieved chunks."""
    plain = "\n\n".join(c["text"] for c in chunks)
    return generate(build_prompt(mode, plain))