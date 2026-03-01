import streamlit as st
import sqlite3
import bcrypt
from groq import Groq

# --- 1. INITIALISATION DES VARIABLES ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- 2. CONFIGURATION RATCOM AI ---
st.set_page_config(page_title="Ratcom AI", page_icon="🤖")

# REMPLACE BIEN gsk_XXX PAR TA CLÉ GROQ
client = Groq(api_key="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")

# --- 3. BASE DE DONNÉES (CORRIGÉ POUR ÉVITER NAMEERROR) ---
def get_db_connection():
    conn = sqlite3.connect('ratcom.db', check_same_thread=False)
    return conn

# Création de la table au démarrage
db_conn = get_db_connection()
db_cursor = db_conn.cursor()
db_cursor.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, phone TEXT UNIQUE, password TEXT)')
db_conn.commit()

# --- 4. INTERFACE DE CONNEXION ---
if not st.session_state.logged_in:
    st.title("🚀 Ratcom AI - Douala")
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab2:
        new_name = st.text_input("Nom complet")
        new_phone = st.text_input("Numéro (ex: 670000000)")
        new_pw = st.text_input("Mot de passe", type='password', key="reg")
        if st.button("S'INSCRIRE"):
            if new_phone and new_pw:
                hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt())
                try:
                    db_cursor.execute("INSERT INTO users VALUES (?,?,?)", (new_name, new_phone, hashed))
                    db_conn.commit()
                    st.success("✅ Compte créé ! Connecte-toi à gauche.")
                except: st.error("❌ Ce numéro est déjà utilisé.")
            else: st.warning("Remplis tous les champs.")

    with tab1:
        phone = st.text_input("Numéro de téléphone")
        pw = st.text_input("Mot de passe", type='password', key="log")
        if st.button("SE CONNECTER"):
            db_cursor.execute("SELECT * FROM users WHERE phone=?", (phone,))
            user = db_cursor.fetchone()
            # On vérifie si l'utilisateur existe et si le mot de passe est bon
            if user and bcrypt.checkpw(pw.encode('utf-8'), user[2]):
                st.session_state.logged_in = True
                st.session_state.username = user[0] # On prend le nom
                st.rerun()
            else: st.error("❌ Numéro ou mot de passe incorrect.")

# --- 5. INTERFACE CHAT IA ---
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
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Appel IA avec modèle récent
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Tu es Ratcom AI, expert à Douala."}] + 
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    model="llama-3.3-70b-versatile",
                )
                res = chat_completion.choices.message.content
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
            except Exception as e: st.error(f"Erreur IA : {e}")
