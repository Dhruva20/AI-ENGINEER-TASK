import streamlit as st

from llm_client import LLMError, generate
from prompts import MODES, build_prompt
from validators import MAX_CHARS, validate_input

st.set_page_config(page_title="StudyBuddy", page_icon="📚")
st.title("📚 StudyBuddy")
st.caption("An AI study assistant for summaries, quizzes, answer feedback and explanations.")

mode = st.radio("What do you want to do?", list(MODES.keys()), horizontal=True)
st.info(MODES[mode]["hint"])

user_input = st.text_area(
    "Your content",
    height=250,
    placeholder="Paste your notes, answer or topic here...",
)
st.caption(f"{len(user_input)} / {MAX_CHARS} characters")

if st.button("Generate", type="primary"):
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