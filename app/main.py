import logging

import streamlit as st

from app.config.settings import SettingsError, get_model_name, load_settings
from app.services.gemini_service import GeminiService, GeminiServiceError
from app.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    st.set_page_config(page_title="AI Question & Answering System", page_icon="💬")
    st.title("AI Question & Answering System")
    st.caption(
        "Ask questions and follow up in a conversation powered by a Google Gemini AI model."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    settings = None
    configuration_error = None
    try:
        settings = load_settings()
    except SettingsError as exc:
        configuration_error = str(exc)
        logger.error("Application configuration is invalid (%s).", type(exc).__name__)

    model_name = settings.model if settings is not None else get_model_name()
    with st.sidebar:
        st.subheader("Conversation")
        st.caption(f"Gemini model: `{model_name}`")
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            logger.info("Conversation cleared.")
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if configuration_error is not None:
        st.error(f"Configuration error: {configuration_error}")
        return

    question = st.chat_input("Type your question")
    if question is None:
        return

    question = question.strip()
    if not question:
        st.warning("Please enter a question before submitting.")
        return

    st.session_state.messages.append({"role": "user", "content": question})
    logger.info(
        "Question submitted (conversation_messages=%d, model=%s).",
        len(st.session_state.messages),
        settings.model,
    )
    with st.chat_message("user"):
        st.markdown(question)

    try:
        if settings is None:
            return
        service = GeminiService(settings)
        with st.chat_message("assistant"):
            with st.spinner("Generating an answer..."):
                answer = service.generate_answer(st.session_state.messages)
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except SettingsError as exc:
        logger.error("Application configuration is invalid (%s).", type(exc).__name__)
        st.error(str(exc))
    except GeminiServiceError as exc:
        logger.error("Answer generation failed (%s).", type(exc).__name__)
        st.error(str(exc))


if __name__ == "__main__":
    main()
