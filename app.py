import streamlit as st
from groq import Groq

# --- CONFIGURATION ---
client = Groq(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Ratcom AI - Douala")

# --- AFFICHAGE CLASSIQUE (ANTI-BUG) ---
# --- AFFICHAGE DE L'HISTORIQUE ---
for chat in st.session_state.history:
    st.markdown(f"👤 **Moi :** {chat['user']}")
    st.info(chat['bot'])
    st.write("---")

# --- ZONE DE SAISIE UNIQUE (SANS DOUBLON) ---
user_input = st.text_area("Pose ta question ici :", height=100, key="unique_input")

if st.button("🚀 ENVOYER À RATCOM AI"):
    if user_input:
        try:
            # On prépare les messages pour l'IA
            messages = [{"role": "system", "content": "Tu es Ratcom AI, expert à Douala."}]
            for h in st.session_state.history:
                messages.append({"role": "user", "content": h["user"]})
                messages.append({"role": "assistant", "content": h["bot"]})
            messages.append({"role": "user", "content": user_input})

            # Appel à Groq
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )
            
            response = completion.choices[0].message.content
            
            # Enregistrement et nettoyage
            st.session_state.history.append({"user": user_input, "bot": response})
            st.experimental_rerun() # Rafraîchit pour afficher la réponse
            
        except Exception as e:
            st.error(f"Erreur : {e}")
    else:
        st.warning("⚠️ Écris d'abord ton message !")

