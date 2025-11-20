import streamlit as st
import json
from src.extraction import extract_articles_and_paragraphs, extract_qa_scope
from src.language import arabic_to_english_translation, english_to_arabic_translation
from src.q_and_a import get_question_summary, get_relevant_context, query_response, vector_db

st.set_page_config(page_title="AI Regulatory Compliance Assistance", layout="wide", initial_sidebar_state="expanded")
st.title("AI Regulatory Compliance Assistance 💬")


if "language" not in st.session_state:
    st.session_state.language = "English"

if "prev_language" not in st.session_state:
    st.session_state.prev_language = "English"

if "prompt" not in st.session_state:
    st.session_state.prompt = None

if "history" not in st.session_state:
    st.session_state.history = []


if "messages" not in st.session_state:
    # st.session_state.messages = messages
    st.session_state.messages = []
    # st.session_state.messages.append(('assistant', messages[0]["content"]))
    # st.session_state.messages.append(('user', messages[1]["content"]))

# Load vectore store and cache
@st.cache_resource
def get_vector_db():
    vector_store = vector_db()
    return vector_store

vector_store = get_vector_db()

with st.sidebar:
    # Choose language (English or Arabic)
    st.markdown("## Settings")
    language = st.selectbox(
        "Language",
        ("English", "Arabic")
    )
    st.session_state.language = language


# ---------- Conversation loop ----------
def run_collection():

    if st.session_state.prompt:
        print("Session Prompt")
        print(st.session_state.prompt)
        print()

        prompt = st.session_state.prompt
        st.session_state.messages.append(('user', prompt))
        st.session_state.history.append(('user', prompt)) # Conversation history
    
        # Get Most resent 
        try:
            scope = extract_qa_scope(st.session_state.prompt)
        except Exception as e:
            scope = True
            print(f"Error in scope extraction: {e}")
        print(f"Scope: {scope}")
        print()

        if not scope:
            string = "Your question is outside the scope of the regulation. Please ask a relevant question."
            st.session_state.messages.append(('assistant', string))
            st.session_state.history.append(('assistant', string))
            return

        if st.session_state.language == "Arabic":
            # Translate to English
            translation = arabic_to_english_translation(st.session_state.prompt)
            prompt = translation["translation"]

        # Summarize question with conversation history
        # format as AI: Human: 
        print(st.session_state.messages[-7:-1])
        conversation_history = []
        # Last 3 messages
        for role, text in st.session_state.history[-7:-1]:
            if role == "user":
                conversation_history.append(f"Human: {text}\n")
            else:
                conversation_history.append(f"AI: {text}\n")
        print("Conversation History:")
        print(conversation_history)
        print()

        try:
            if conversation_history == []:
                question_summary = st.session_state.prompt
            else:
                question_summary = get_question_summary(st.session_state.prompt, conversation_history)
        
        except Exception as e:
            question_summary = st.session_state.prompt
            print(f"Error in question summarization: {e}")

        print("Question Summary:")
        print(question_summary)
        print()

        # Get relevant context
        relevant_context = get_relevant_context(question_summary, vector_store)
        print("Relevant Context:")
        print(relevant_context)
        print()

        # Get final answer
        response = query_response(prompt, conversation_history, relevant_context)
        message = response["answer"]
        print("Final Response:")
        print(json.dumps(response, indent=2))
        print()

        # Translate back to Arabic if needed
        if st.session_state.language == "Arabic":
            message = english_to_arabic_translation(message)["translation"]
        # If references present in response, append them
        new_message = message
        if response["citations"]:
            new_message += "\n\nReferences:\n"
            for citation in response["citations"]:
                article = citation["article"]
                paragraph = citation["paragraph"]
                text = citation["text"]
                new_message += f"- Article {article}, Paragraph {paragraph}: {text}\n"
            
        # print(f"Message\n {message}")
        st.session_state.messages.append(('assistant', new_message))
        st.session_state.history.append(('assistant', message))


# Reset chat if language changed
if st.session_state.language != st.session_state.prev_language:
    # Clear chat history and messages
    st.session_state.history = []
    st.session_state.messages = []
    st.session_state.prev_language = st.session_state.language

    for role, text in st.session_state.messages:
        st.chat_message(role).write(text)


# Input area for user queries
if len(st.session_state.messages) < 2:
    run_collection()

st.chat_input("Enter your query", key='prompt', on_submit=run_collection)

# Display chat messages

# with message:
for role, text in st.session_state.messages:
    st.chat_message(role).write(text)