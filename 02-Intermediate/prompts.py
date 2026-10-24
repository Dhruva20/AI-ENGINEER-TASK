MODES = {
    "Summarize notes": {
        "hint": "Paste your class notes and get a short summary with key points.",
        "template": """You are a helpful study assistant for students.

TASK: Summarize the notes below.

FORMAT:
- A 2-3 sentence overview
- 4-6 bullet points of key ideas
- A "Key terms" line listing important terms

RULES: Use simple language. Only use information from the notes. Do not invent facts.

NOTES:
{user_input}""",
    },
    "Generate quiz": {
        "hint": "Paste your notes and get 5 multiple-choice questions.",
        "template": """You are a teacher creating a practice quiz.

TASK: Create 5 multiple-choice questions from the notes below.

FORMAT for each question:
Q1. <question>
A) ... B) ... C) ... D) ...
Answer: <letter>
Explanation: <one sentence>

RULES: Base every question only on the notes. Make wrong options plausible.

NOTES:
{user_input}""",
    },
    "Improve my answer": {
        "hint": "Paste an exam answer and get a stronger version with feedback.",
        "template": """You are an exam coach helping a student improve a written answer.

TASK: Review the answer below.

FORMAT:
1. **Feedback** - 3 short bullets on what is weak (clarity, structure, missing points)
2. **Improved answer** - a rewritten, better version
3. **Why it's better** - one sentence

RULES: Keep the student's meaning. Do not add unrelated facts.

STUDENT ANSWER:
{user_input}""",
    },
    "Explain a concept": {
        "hint": "Type a topic or question and get a simple explanation.",
        "template": """You are a patient tutor explaining to a first-year student.

TASK: Explain the topic or question below.

FORMAT:
- **Simple explanation** (3-4 sentences)
- **Real-life example**
- **Common mistake to avoid**

RULES: Use plain language. If the topic is unclear, say what you assumed.

TOPIC:
{user_input}""",
    },
}


def build_prompt(mode: str, user_input: str) -> str:
    return MODES[mode]["template"].format(user_input=user_input.strip())

RAG_TEMPLATE = """You are a careful study assistant that answers using ONLY the context below.

RULES:
- Use only the information in the CONTEXT. Do not use outside knowledge.
- If the context does not contain the answer, reply exactly: "{no_answer}"
- Keep the answer clear and concise.
- After each fact, cite the passage number like [1] or [2].

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""


def build_rag_prompt(question: str, context: str, no_answer: str) -> str:
    return RAG_TEMPLATE.format(no_answer=no_answer, context=context, question=question.strip())