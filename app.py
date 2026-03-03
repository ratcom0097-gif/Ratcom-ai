import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION GROQ ---
# REMPLACE BIEN PAR TA CLÉ gsk_
client = Groq(api_key="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")

# Initialisation de l'historique
if "history" not in st.session_state:
    st.session_state.history = []

# --- 2. INTERFACE RATCOM AI ---
st.title("🤖 Ratcom AI - Douala")
st.write("L'IA experte du pays à ton service.")

# --- 3. AFFICHAGE DES MESSAGES (STABLE) ---
for chat in st.session_state.history:
    st.info(f"👤 **Moi :** {chat['user']}")
    st.success(f"🤖 **Ratcom AI :** {chat['bot']}")

# --- 4. ZONE DE SAISIE SIMPLE ---
user_input = st.text_area("Pose ta question ici :", height=100, key="input_unique")

if st.button("🚀 ENVOYER"):
    if user_input:
        try:
            # Préparation des messages
            messages = [{"role": "system", "content": "Tu es Ratcom AI, expert à Douala."}]
            for h in st.session_state.history:
                messages.append({"role": "user", "content": h["user"]})
                messages.append({"role": "assistant", "content": h["bot"]})
            messages.append({"role": "user", "content": user_input})

            # Appel IA
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )
            response = completion.choices[0].message.content
            
            # Enregistrement
            st.session_state.history.append({"user": user_input, "bot": response})
            st.rerun() # Rafraîchit l'affichage
            
        except Exception as e:
            st.error(f"Erreur : {e}")
    else:
        st.warning("Écris un message d'abord !")

# Bouton pour tout effacer
if st.sidebar.button("🗑️ Effacer la discussion"):
    st.session_state.history = []
    st.rerun()
