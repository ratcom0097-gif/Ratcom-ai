import streamlit as st
import sqlite3
import bcrypt
from groq import Groq
import os

# --- 1. INITIALISATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_display' not in st.session_state:
    st.session_state.user_display = ""

st.set_page_config(page_title="Ratcom AI", page_icon="🤖")

# --- 2. BASE DE DONNÉES ---
# Note: Sur Streamlit Cloud, ce fichier sera réinitialisé à chaque déploiement
def get_db():
    conn = sqlite3.connect('ratcom_data.db', check_same_thread=False)
    return conn

db = get_db()
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (fullname TEXT, phone TEXT UNIQUE, password TEXT)')
db.commit()

# --- 3. CONFIGURATION IA ---
# Remplace par ta clé gsk_
client = Groq(api_key="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")

# --- 4. INTERFACE CONNEXION / INSCRIPTION ---
if not st.session_state.logged_in:
    st.title("🚖 Ratcom AI - Douala")
    tab1, tab2 = st.tabs(["Se Connecter", "Créer un Compte"])

    with tab2:
        st.subheader("Nouvel Utilisateur")
        reg_name = st.text_input("Nom Complet", key="n1")
        reg_phone = st.text_input("Numéro de Téléphone", key="n2")
        reg_pw = st.text_input("Mot de passe", type='password', key="n3")
        
        if st.button("S'INSCRIRE"):
            if reg_phone and reg_pw:
                # Hachage du mot de passe
                hashed = bcrypt.hashpw(reg_pw.encode('utf-8'), bcrypt.gensalt())
                try:
                    cursor.execute("INSERT INTO users VALUES (?,?,?)", (reg_name, reg_phone, hashed))
                    db.commit()
                    st.success("✅ Compte créé ! Connectez-vous maintenant.")
                except:
                    st.error("❌ Ce numéro est déjà utilisé.")
            else:
                st.warning("⚠️ Remplissez tous les champs.")

    with tab1:
        st.subheader("Accès Client")
        log_phone = st.text_input("Numéro", key="l1")
        log_pw = st.text_input("Mot de passe", type='password', key="l2")
        
        if st.button("LOG IN"):
            cursor.execute("SELECT fullname, password FROM users WHERE phone=?", (log_phone,))
            result = cursor.fetchone()
            
            if result:
                # result[0] = Nom, result[1] = Mot de passe haché
                if bcrypt.checkpw(log_pw.encode('utf-8'), result[1]):
                    st.session_state.logged_in = True
                    st.session_state.user_display = result[0]
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect.")
            else:
                st.error("❌ Numéro non reconnu. Inscrivez-vous d'abord.")

# --- 5. INTERFACE CHAT ---
else:
    st.sidebar.title(f"👤 {st.session_state.user_display}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🤖 Assistant Ratcom AI")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Pose ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # On force l'IA à être experte du Cameroun
                sys_msg = {"role": "system", "content": "Tu es Ratcom AI, expert du Cameroun à Douala."}
                full_history = [sys_msg] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=full_history
                )
                res = chat.choices[0].message.content
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
            except Exception as e:
                st.error(f"Erreur : {e}")
