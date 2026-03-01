import streamlit as st
from openai import OpenAI

# --- 1. CONFIGURATION GROQ (L'ADRESSE EXACTE) ---
# REMPLACE LE TEXTE CI-DESSOUS PAR TA CLÉ GSK_
MY_API_KEY = "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" 

client = OpenAI(
    api_key=MY_API_KEY,
    base_url="https://api.groq.com"
)

# --- 2. INTERFACE RATCOM AI ---
st.set_page_config(page_title="Ratcom AI", page_icon="🤖")
st.title("🤖 Ratcom AI - Douala")
st.write("Pose ta question ici :")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 3. ZONE DE CHAT ---
if prompt := st.chat_input("Dis quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # On utilise le modèle Llama3 qui est gratuit et rapide
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            full_res = response.choices[0].message.content
            st.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"Oups ! Erreur de connexion : {e}")
