import streamlit as st
import sqlite3
import bcrypt
from openai import OpenAI

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ratcom AI", page_icon="🚀")

# --- 2. TA CLÉ API (VERIFIE BIEN ICI) ---
# Si tu as une clé GROQ (commence par gsk_) :
MY_API_KEY = "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" 

client = OpenAI(
    api_key=MY_API_KEY,
    base_url="https://api.groq.com/v1" # Enlève cette ligne si tu utilises OpenAI (sk-)
)

# --- 3. BASE DE DONNÉES ---
conn = sqlite3.connect('ratcom.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, phone TEXT UNIQUE, password TEXT)')
conn.commit()

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- 5. INTERFACE CONNEXION ---
if not st.session_state.logged_in:
    st.title("🚖 Ratcom AI - Douala")
    menu = ["Connexion", "Inscription"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Inscription":
        name = st.text_input("Nom")
        phone = st.text_input("Téléphone")
        pw = st.text_input("Mot de passe", type='password')
        if st.button("S'inscrire"):
            h_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
            try:
                c.execute("INSERT INTO users VALUES (?,?,?)", (name, phone, h_pw))
                conn.commit()
                st.success("Compte créé ! Connecte-toi.")
            except: st.error("Numéro déjà utilisé.")

    else:
        phone = st.text_input("Téléphone")
        pw = st.text_input("Mot de passe", type='password')
        if st.button("Se connecter"):
            c.execute("SELECT * FROM users WHERE phone=?", (phone,))
            user = c.fetchone()
            if user and bcrypt.checkpw(pw.encode('utf-8'), user[2]):
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.rerun()
            else: st.error("Erreur de connexion.")

# --- 6. INTERFACE CHAT (RATCOM AI) ---
else:
    st.title(f"🤖 Bienvenue {st.session_state.username}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Pose ta question à Ratcom AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Modèle pour Groq : llama3-8b-8192
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
                full_res = response.choices[0].message.content
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error(f"Erreur : {e}")
