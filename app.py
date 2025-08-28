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

# ====== BARU: Bagian Prompt Engineering di Sidebar ======
st.sidebar.header("🤖 Prompt Engineering")
st.sidebar.caption("Based on the 6-Step Prompt Checklist")

# Persona
persona = st.sidebar.text_input(
    "Persona", 
    placeholder="e.g., a helpful AI assistant for Python programming"
)

# Context
context = st.sidebar.text_area(
    "Context",
    placeholder="Provide background information or constraints..."
)

# Examples
examples = st.sidebar.text_area(
    "Examples",
    placeholder="User: What is Streamlit?\nAI: Streamlit is an open-source Python library..."
)

# Format
# Menggunakan format_ untuk menghindari konflik dengan fungsi built-in format()
format_ = st.sidebar.selectbox(
    "Format",
    ["", "Markdown", "JSON", "Bullet Points", "Table"]
)

# Tone
tone = st.sidebar.selectbox(
    "Tone",
    ["", "Formal", "Casual", "Humorous", "Professional", "Sarcastic"]
)
# ==========================================================


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
    # Tambahkan pesan user ke chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Tampilkan pesan user di chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # ====== BARU: Konstruksi System Prompt dari Input Sidebar ======
    system_prompt_parts = []
    if persona:
        system_prompt_parts.append(f"Embody this persona: {persona}.")
    if context:
        system_prompt_parts.append(f"Consider the following context: {context}.")
    if examples:
        system_prompt_parts.append(f"Follow these examples:\n{examples}.")
    if format_:
        system_prompt_parts.append(f"Format your response as {format_}.")
    if tone:
        system_prompt_parts.append(f"Your tone should be {tone}.")

    # Gabungkan semua bagian menjadi satu system prompt
    system_prompt_content = " ".join(system_prompt_parts)

    # Buat list pesan baru untuk dikirim ke API
    messages_for_api = []
    if system_prompt_content:
        messages_for_api.append({"role": "system", "content": system_prompt_content})
    
    # Tambahkan riwayat chat yang sudah ada
    messages_for_api.extend(st.session_state.messages)
    # ===============================================================

    # Tambahkan st.spinner() di sini
    with st.spinner("Thinking..."):
        # Panggil API dan dapatkan respons
        # ====== MODIFIKASI: Gunakan messages_for_api ======
        full_response = call_openrouter(
            model_choice,
            messages_for_api, # Menggunakan pesan yang sudah dimodifikasi
            temperature,
            top_p,
            top_k,
            max_tokens
        )
    
    # Setelah spinner selesai, tampilkan respons
    with st.chat_message("assistant"):
        st.markdown(full_response)
        
    # Simpan respons ke session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Tombol summarize
if st.sidebar.button("📝 Summarize Chat"):
    with st.spinner("Summarizing..."):
        # Cek jika ada riwayat chat untuk diringkas
        if len(st.session_state.messages) > 0:
            summary_prompt = [
                {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                {"role": "user", "content": f"Please summarize this conversation:\n\n{st.session_state.messages}"}
            ]
            summary = call_openrouter(model_choice, summary_prompt)
            
            # Tampilkan di chat
            with st.chat_message("assistant"):
                st.markdown(f"**Conversation Summary:**\n\n{summary}")
            
            # Simpan ringkasan ke session state
            st.session_state.messages.append({"role": "assistant", "content": f"**Conversation Summary:**\n\n{summary}"})
        else:
            st.warning("There is no conversation to summarize yet.")
