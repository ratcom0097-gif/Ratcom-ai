import streamlit as st
import sqlite3
import bcrypt
from groq import Groq

# --- 1. INITIALISATION DE LA SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- 2. CONFIGURATION RATCOM AI ---
st.set_page_config(page_title="Ratcom AI", page_icon="🤖")

# REMPLACE PAR TA CLÉ GROQ RÉELLE (gsk_...)
MY_API_KEY = "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"
client = Groq(api_key=MY_API_KEY)

# --- 3. GESTION DE LA BASE DE DONNÉES ---
def get_db():
    conn = sqlite3.connect('ratcom.db', check_same_thread=False)
    return conn

db_conn = get_db()
cursor = db_conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, phone TEXT UNIQUE, password TEXT)')
db_conn.commit()

# --- 4. INTERFACE DE CONNEXION / INSCRIPTION ---
if not st.session_state.logged_in:
    st.title("🚖 Ratcom AI - Douala")
    st.write("L'IA experte du Cameroun.")
    
    tab1, tab2 = st.tabs(["Se Connecter", "Créer un Compte"])

    with tab2:
        st.subheader("Inscription")
        new_name = st.text_input("Nom complet", key="reg_name")
        new_phone = st.text_input("Numéro (ex: 670000000)", key="reg_phone")
        new_pw = st.text_input("Mot de passe", type='password', key="reg_pw")
        
        if st.button("S'INSCRIRE"):
            if new_phone and new_pw:
                hashed_pw = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt())
                try:
                    cursor.execute("INSERT INTO users VALUES (?,?,?)", (new_name, new_phone, hashed_pw))
                    db_conn.commit()
                    st.success("✅ Compte créé ! Connecte-toi à gauche.")
                except:
                    st.error("❌ Ce numéro est déjà utilisé.")
            else:
                st.warning("⚠️ Remplis tous les champs.")

    with tab1:
        st.subheader("Connexion")
        login_phone = st.text_input("Numéro de téléphone", key="log_phone")
        login_pw = st.text_input("Mot de passe", type='password', key="log_pw")
        
        if st.button("LOG IN"):
            cursor.execute("SELECT name, password FROM users WHERE phone=?", (login_phone,))
            user_data = cursor.fetchone()
            
            if user_data:
                # user_data[1] contient le mot de passe haché
                if bcrypt.checkpw(login_pw.encode('utf-8'), user_data[1]):
                    st.session_state.logged_in = True
                    st.session_state.username = user_data[0] # Nom de l'utilisateur
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect.")
            else:
                st.error("❌ Numéro non trouvé. Inscris-toi d'abord.")

# --- 5. INTERFACE CHAT IA ---
else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

    st.title("🤖 Ratcom AI Expert")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Pose ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                system_prompt = {"role": "system", "content": "Tu es Ratcom AI, expert du Cameroun à Douala."}
                history = [system_prompt] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history,
                )
                
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Erreur IA : {e}")
