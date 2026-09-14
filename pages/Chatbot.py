import os
import sys
import streamlit as st

# Make backend importable
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from cocare import process_message


st.set_page_config(
    page_title="CoCare AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 CoCare AI Assistant")
st.caption("Arabic & English Telecom Customer Support")


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_message = st.chat_input(
    "اكتب رسالتك هنا... / Type your message here..."
)

if user_message:

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.markdown(user_message)

    try:
        result = process_message(
            user_message=user_message,
            user_id="demo_customer",
            region="Amman"
        )

        response = result.get(
            "response",
            "Sorry, I could not process your request."
        )

        followup = result.get("followup_response")

        full_response = response

        if followup:
            full_response += f"\n\n{followup}"

    except Exception as exc:
        full_response = (
            "حدث خطأ أثناء معالجة الرسالة. "
            "Please try again."
        )

        print("Chatbot error:", exc)

    with st.chat_message("assistant"):
        st.markdown(full_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
