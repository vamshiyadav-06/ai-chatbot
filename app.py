import json
import os
import urllib.error
import urllib.request

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY") or os.environ.get("GROQ_API_KEY")
provider = "groq" if api_key and api_key.startswith("gsk_") else "grok"
client = bool(api_key and api_key != "your_grok_api_key_here")

st.set_page_config(page_title="AI Custom Assistant", page_icon="🤖", layout="centered")

st.markdown(
    """
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🤖 Custom AI Assistant")

with st.sidebar:
    st.header("⚙️ Settings")
    system_prompt_choice = "Friend"
    system_prompt = (
        "You are a supportive, casual, and empathetic friend. "
        "Use conversational language, emojis, and be very relatable."
    )
    st.markdown(f"**Persona:** {system_prompt_choice}")

    st.markdown("---")
    st.markdown("**About this app:**")
    st.markdown("This chatbot uses Streamlit and the Grok API to maintain real-time conversational history.")

    st.markdown("---")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not client:
    st.warning("⚠️ Please set `GROK_API_KEY` / `XAI_API_KEY` / `GROQ_API_KEY` in `.env` to use this chatbot.")
    st.info("Get keys from [xAI Console](https://console.x.ai/) or [Groq Console](https://console.groq.com/keys).")
else:
    st.success(f"Connected provider: {'Groq' if provider == 'groq' else 'Grok/xAI'}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if client:
        messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages:
            messages.append(
                {
                    "role": "assistant" if msg["role"] == "assistant" else "user",
                    "content": msg["content"],
                }
            )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                with st.spinner("Thinking..."):
                    endpoint = (
                        "https://api.groq.com/openai/v1/chat/completions"
                        if provider == "groq"
                        else "https://api.x.ai/v1/chat/completions"
                    )
                    model_name = "llama-3.1-8b-instant" if provider == "groq" else "grok-3-mini"
                    payload = json.dumps(
                        {"model": model_name, "messages": messages, "temperature": 0.7}
                    ).encode("utf-8")
                    request = urllib.request.Request(
                        endpoint,
                        data=payload,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-Streamlit-App",
                            "Authorization": f"Bearer {api_key}",
                        },
                        method="POST",
                    )
                    with urllib.request.urlopen(request, timeout=60) as response:
                        response_body = response.read().decode("utf-8")

                response_json = json.loads(response_body)
                full_response = (
                    response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                )

                if not full_response:
                    full_response = "No response content returned by provider."
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except urllib.error.HTTPError as e:
                error_body = ""
                try:
                    error_body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    error_body = ""
                st.error(f"Provider API HTTP error: {e.code} - {e.reason}. {error_body[:300]}")
            except Exception as e:
                st.error(f"An API error occurred: {str(e)}")
