import streamlit as st
import requests

# ====== CONFIGURASI API ======
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ====== FUNGSI REQUEST KE OPENROUTER ======
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

# ====== STREAMLIT UI ======
st.set_page_config(page_title="Chatbot with OpenRouter", layout="wide")

st.markdown("<h1 style='text-align: center;'>🤖 GemOpen</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Settings")

# Pilihan model
model_choice = st.sidebar.selectbox(
    "Choose Model",
    ["google/gemini-flash-1.5-8b", "openai/gpt-4o-mini"]
)

# Advanced settings
with st.sidebar.expander("Advanced Settings"):
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    top_p = st.slider("Top-P", 0.0, 1.0, 1.0)
    top_k = st.slider("Top-K", 1, 100, 40)
    max_tokens = st.slider("Max Tokens", 50, 2000, 500)

# Riwayat chat (session state)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input user
if prompt := st.chat_input("Ketik pesan Anda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Panggil API
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = call_openrouter(
                model_choice,
                st.session_state.messages,
                temperature,
                top_p,
                top_k,
                max_tokens
            )
            st.markdown(reply)

    # Simpan jawaban AI
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Tombol summarize
if st.sidebar.button("📝 Summarize Chat"):
    with st.spinner("Summarizing..."):
        summary_prompt = [
            {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
            {"role": "user", "content": f"Please summarize this conversation:\n\n{st.session_state.messages}"}
        ]
        summary = call_openrouter(model_choice, summary_prompt)
        
        # Simpan ringkasan di session_state
        st.session_state.messages.append({"role": "assistant", "content": summary})
        
        # Tampilkan di chat
        with st.chat_message("assistant"):
            st.markdown(summary)
