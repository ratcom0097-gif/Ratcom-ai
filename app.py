import streamlit as st
import sqlite3
import bcrypt
from openai import OpenAI

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Ratcom AI", page_icon="🚀", layout="centered")

# --- 2. BASE DE DONNÉES (SÉCURITÉ) ---
def create_db():
    conn = sqlite3.connect('ratcom.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT, phone TEXT UNIQUE, password TEXT, is_pro BOOLEAN)''')
    conn.commit()
    conn.close()

def hash_pw(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_pw(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# --- 3. LOGIQUE IA (CLÉ API) ---
# Remplace 'VOTRE_CLE_ICI' par ta vraie clé OpenAI ou Groq
client = OpenAI(api_key="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")

# --- 4. INTERFACE UTILISATEUR ---
create_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- PAGE DE CONNEXION ---
if not st.session_state['logged_in']:
    st.title("🚖 Ratcom AI - Douala")
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab2:
        new_user = st.text_input("Nom complet")
        new_phone = st.text_input("Numéro (6xxxxxxxx)")
        new_pw = st.text_input("Mot de passe", type='password', key="reg")
        if st.button("Créer mon compte"):
            conn = sqlite3.connect('ratcom.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?,?,?,?)", (new_user, new_phone, hash_pw(new_pw), False))
                conn.commit()
                st.success("Compte créé ! Connecte-toi maintenant.")
            except:
                st.error("Ce numéro existe déjà.")
            conn.close()

    with tab1:
        login_phone = st.text_input("Numéro de téléphone")
        login_pw = st.text_input("Mot de passe", type='password', key="log")
        if st.button("Se connecter"):
            conn = sqlite3.connect('ratcom.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone=?", (login_phone,))
            user = c.fetchone()
            conn.close()
            if user and check_pw(login_pw, user[2]):
                st.session_state['logged_in'] = True
                st.session_state['user'] = user[0]
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

# --- PAGE CHAT IA (APRÈS CONNEXION) ---
else:
    st.sidebar.title(f"Salut, {st.session_state['user']} !")
    if st.sidebar.button("Déconnexion"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🤖 Ratcom AI")
    st.write("Pose-moi tes questions sur Douala, le business ou la tech.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ecris ici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Ici on simule ou on appelle l'IA
            response = "Je suis Ratcom AI, ton assistant intelligent à Douala. Comment puis-je t'aider ?"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
