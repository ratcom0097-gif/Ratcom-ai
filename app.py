import streamlit as st
import sqlite3
import bcrypt
from groq import Groq
from gtts import gTTS
import base64
import os

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Ratcom AI", page_icon="🤖")

# Style CSS pour le fond sombre et les boutons bleus (Style Google Tech)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #1c2531 100%); color: white; }
    .stChatMessage { border-radius: 15px; border: 1px solid #262730; background-color: #161b22; }
    div.stButton > button { background-color: #4285F4; color: white; border-radius: 10px; width: 100%; border: none; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #0d1117; color: white; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALISATION SESSION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'user_display' not in st.session_state: st.session_state.user_display = ""

# --- 3. FONCTION VOCALE (AUDIO) ---
def parler(texte):
    try:
        # On limite à 200 caractères pour la rapidité
        tts = gTTS(text=texte[:200], lang='fr')
        tts.save("voix.mp3")
        with open("voix.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        os.remove("voix.mp3")
    except: pass

# --- 4. BASE DE DONNÉES ---
conn = sqlite3.connect('ratcom_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, phone TEXT UNIQUE, password TEXT)')
conn.commit()

# --- 5. CONFIGURATION IA (GROQ) ---
# REMPLACE PAR TA CLÉ gsk_
client = Groq(api_key="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")

# --- 6. INTERFACE CONNEXION / INSCRIPTION ---
if not st.session_state.logged_in:
    st.title("🚖 Ratcom AI - Douala")
    tab1, tab2 = st.tabs(["Se Connecter", "Créer un Compte"])

    with tab2:
        n_name = st.text_input("Nom Complet", key="n1")
        n_phone = st.text_input("Numéro (ex: 670000000)", key="n2")
        n_pw = st.text_input("Mot de passe", type='password', key="n3")
        if st.button("S'INSCRIRE"):
            if n_phone and n_pw:
                hashed = bcrypt.hashpw(n_pw.encode('utf-8'), bcrypt.gensalt())
                try:
                    c.execute("INSERT INTO users VALUES (?,?,?)", (n_name, n_phone, hashed))
                    conn.commit()
                    st.success("✅ Compte créé ! Connecte-toi.")
                except: st.error("❌ Numéro déjà utilisé.")

    with tab1:
        l_phone = st.text_input("Numéro", key="l1")
        l_pw = st.text_input("Mot de passe", type='password', key="l2")
        if st.button("ACCÉDER À RATCOM AI"):
            c.execute("SELECT name, password FROM users WHERE phone=?", (l_phone,))
            res = c.fetchone()
            if res and bcrypt.checkpw(l_pw.encode('utf-8'), res[1]):
                st.session_state.logged_in = True
                st.session_state.user_display = res[0]
                st.rerun()
            else: st.error("❌ Identifiants incorrects.")

# --- 7. INTERFACE CHAT IA ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_display}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

    st.title("🤖 Ratcom AI Expert")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Pose ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                sys_msg = {"role": "system", "content": "Tu es Ratcom AI, expert du Cameroun à Douala. Réponds brièvement."}
                history = [sys_msg] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                
                completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=history)
                response = completion.choices[0].message.content
                st.markdown(response)
                parler(response) # L'IA parle
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e: st.error(f"Erreur : {e}")
