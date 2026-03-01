import streamlit as st
from groq import Groq

# --- CONFIGURATION RATCOM AI ---
st.set_page_config(page_title="Ratcom AI", page_icon="🤖")

# --- INITIALISATION CLIENT (SANS URL MANUELLE) ---
# REMPLACE BIEN gsk_XXX PAR TA CLÉ RÉELLE
client = Groq(api_key="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")

st.title("🤖 Ratcom AI - Douala")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- ZONE DE CHAT ---
if prompt := st.chat_input("Dis quelque chose à Ratcom AI..."):
    # On ajoute le message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse de l'assistant (BIEN ALIGNÉ ICI)
    with st.chat_message("assistant"):
        try:
            instructions = {
                "role": "system", 
                "content": "Tu es Ratcom AI, l'expert n°1 du Cameroun basé à Douala. Réponds comme un conseiller local."
            }
            
            envoi = [instructions] + [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=envoi,
            )
            
            reponse = completion.choices[0].message.content
            st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})
            
        except Exception as e:
            st.error(f"Erreur technique : {e}")
        except Exception as e:
            st.error(f"Erreur technique : {e}")
