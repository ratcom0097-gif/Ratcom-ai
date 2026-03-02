import streamlit as st
from groq import Groq

# --- CONFIGURATION ---
client = Groq(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Ratcom AI - Douala")

# --- AFFICHAGE CLASSIQUE (ANTI-BUG) ---
for m in st.session_state.messages:
    if m["role"] == "user":
        st.info(f"👤 **Moi :** {m['content']}")
    else:
        st.success(f"🤖 **Ratcom AI :** {m['content']}")

# --- ZONE DE TEXTE SIMPLE ---
with st.form("my_form", clear_on_submit=True):
    user_input = st.text_input("Pose ta question ici :")
    submit = st.form_submit_button("Envoyer")

if submit and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es Ratcom AI, expert à Douala."}] + 
                     [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        )
        response = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun() # Recharge la page pour afficher la réponse
    except Exception as e:
        st.error(f"Erreur : {e}")
