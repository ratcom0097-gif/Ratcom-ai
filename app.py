import streamlit as st
from groq import Groq
import hmac # Pour sécuriser l'accès sans base de données complexe au début

# --- 1. CONFIGURATION ÉLÉGANTE ---
st.set_page_config(page_title="Ratcom AI", page_icon="🧠", layout="wide")

# Style "Minimaliste Pro" (Fond sombre, texte clair, design fluide)
# --- STYLE GOOGLE MODERNE (FOND CLAIR) ---
st.markdown("""
    <style>
    /* Fond principal gris très clair (Google Style) */
    .stApp {
        background-color: #F8F9FA;
        color: #202124;
    }
    /* Bulles de chat style "Cartes" blanches */
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 15px;
        border: 1px solid #E0E0E0;
        color: #202124;
    }
    /* Style du texte utilisateur */
    .stMarkdown {
        font-family: 'Roboto', sans-serif;
    }
    /* Boutons Bleus Google */
    div.stButton > button {
        background-color: #1A73E8;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #1765CC;
        box-shadow: 0 1px 2px rgba(60,64,67,0.3);
    }
    /* Barre de saisie */
    .stChatInput {
        border-top: 1px solid #E0E0E0;
        background-color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 2. INITIALISATION DE L'IA ---
client = Groq(api_key="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")

if "messages" not in st.session_state:
    # L'instruction système qui me définit comme ton partenaire
    st.session_state.messages = [
        {"role": "system", "content": "Tu es Ratcom AI, un collaborateur authentique, adaptatif et concis. "
                                      "Ton but est d'aider les utilisateurs camerounais avec insight et clarté. "
                                      "Tu parles un français naturel, parfois avec des expressions locales si approprié. "
                                      "Sois succinct, organisé et évite les longs blocs de texte."}
    ]

# --- 3. INTERFACE DE CHAT ---
st.title("🚀 Ratcom AI")
st.caption("Ton partenaire intelligent à Douala")

# Affichage de l'historique (on cache le message 'system')
# --- AFFICHAGE DES MESSAGES (VERSION COMPATIBLE) ---
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    # On utilise une structure simple sans trop de CSS complexe
    if role == "user":
        st.info(f"👤 Toi : {content}")
    elif role == "assistant":
        st.success(f"🤖 Ratcom AI : {content}")

# Zone de saisie
if prompt := st.chat_input("Comment puis-je t'aider aujourd'hui ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Appel au modèle le plus puissant (70B)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.7, # Pour être plus créatif et humain
                max_tokens=1024
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

# Bouton pour effacer la mémoire
if st.sidebar.button("Effacer la discussion"):
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()
