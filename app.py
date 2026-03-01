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

        # --- LA PARTIE DU CHAT BIEN ALIGNÉE ---
        with st.chat_message("assistant"):
            try:
                # Instructions pour l'IA
                system_prompt = {"role": "system", "content": "Tu es Ratcom AI, expert à Douala."}
                
                # Préparation des messages
                messages_history = [system_prompt] + [
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages
                ]

                # Appel à Groq
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_history
                )
                
                # Récupération de la réponse (avec [0] pour éviter l'erreur 'list')
                response = completion.choices[0].message.content
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Erreur IA : {e}")
