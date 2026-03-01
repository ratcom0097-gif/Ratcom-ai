import streamlit as st
from groq import Groq

# --- CONFIGURATION RATCOM AI ---
st.set_page_config(page_title="Ratcom AI", page_icon="🤖")

# --- INITIALISATION CLIENT (SANS URL MANUELLE) ---
# REMPLACE BIEN gsk_XXX PAR TA CLÉ RÉELLE
client = Groq(api_key="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")

st.title("🤖 Ratcom AI - Douala")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages
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
            # Appel simplifié
            completion = client.chat.completions.create(
                model="llama-3.3-70b-specdec",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Erreur technique : {e}")
