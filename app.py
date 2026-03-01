import streamlit as st
from groq import Groq

# --- CONFIGURATION RATCOM AI ---
st.set_page_config(page_title="Ratcom AI", page_icon="🤖")

# METS TA CLÉ gsk_ ICI
client = Groq(api_key="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")

st.title("🤖 Ratcom AI - Douala")
st.write("Pose ta question à ton assistant intelligent :")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les anciens messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- ZONE DE CHAT ---
if prompt := st.chat_input("Dis quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Appel direct via la bibliothèque Groq (Zéro erreurONS  404)
            chat_completion = client.chat.completions.create(
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                model="llama3-8b-8192",
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
