import streamlit as st
import requests

# ===== CONFIGURASI API =====
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ===== FUNGSI REQUEST KE OPENROUTER =====
def call_openrouter(model, messages, temperature=0.7, top_p=1, top_k=40, max_tokens=500):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.text}"

# ===== STREAMLIT UI =====
st.set_page_config(page_title="Chatbot with OpenRouter", layout="wide")

st.markdown("<h1 style='text-align:center; color:#4B8BBE;'>🤖 Multi-Model Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#306998;'>Gemini & GPT via OpenRouter</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Chat Settings")

# Pilihan model
model_choice = st.sidebar.selectbox(
    "Choose AI Model",
    ["google/gemini-flash-1.5-8b", "openai/gpt-4o-mini"]
)

# Advanced settings
with st.sidebar.expander("Advanced Settings"):
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    top_p = st.slider("Top-P", 0.0, 1.0, 1.0)
    top_k = st.slider("Top-K", 1, 100, 40)
    max_tokens = st.slider("Max Tokens", 50, 2000, 500)

# Tombol reset chat
if st.sidebar.button("🧹 Reset Chat"):
    st.session_state.messages = []
    st.experimental_rerun()

# Tombol summarize
if st.sidebar.button("📝 Summarize Chat"):
    if st.session_state.get("messages"):
        with st.spinner("Summarizing..."):
            summary_prompt = [
                {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                {"role": "user", "content": f"Please summarize this conversation:\n\n{st.session_state['messages']}"}
            ]
            summary = call_openrouter(model_choice, summary_prompt)
            st.sidebar.success(summary)
    else:
        st.sidebar.warning("Chat history is empty!")

# Riwayat chat (session state)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan chat history dengan tampilan berbeda
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='background-color:#DCF8C6; padding:10px; border-radius:10px; margin-bottom:5px;'>**You:** {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color:#F1F0F0; padding:10px; border-radius:10px; margin-bottom:5px;'>**AI:** {msg['content']}</div>", unsafe_allow_html=True)

# Input user
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Tampilkan pesan user
    st.markdown(f"<div style='background-color:#DCF8C6; padding:10px; border-radius:10px; margin-bottom:5px;'>**You:** {prompt}</div>", unsafe_allow_html=True)

    # Panggil API
    with st.spinner("AI is thinking..."):
        reply = call_openrouter(
            model_choice,
            st.session_state.messages,
            temperature,
            top_p,
            top_k,
            max_tokens
        )
        st.markdown(f"<div style='background-color:#F1F0F0; padding:10px; border-radius:10px; margin-bottom:5px;'>**AI:** {reply}</div>", unsafe_allow_html=True)

    # Simpan jawaban AI
    st.session_state.messages.append({"role": "assistant", "content": reply})
