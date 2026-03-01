import streamlit as st
from groq import Groq
import hmac # Pour sécuriser l'accès sans base de données complexe au début

# --- 1. CONFIGURATION ÉLÉGANTE ---
st.set_page_config(page_title="Ratcom AI", page_icon="🧠", layout="wide")

# Style "Minimaliste Pro" (Fond sombre, texte clair, design fluide)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    .stChatMessage { border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: #111111; border: 1px solid #222; }
    .stChatInput { border-top: 1px solid #333; padding-top: 20px; }
    button { border-radius: 20px !important; text-transform: uppercase; font-weight: bold; }
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
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
