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
# --- BOUTON DE PARTAGE WHATSAPP (VIRALITÉ DOUALA) ---
st.divider() # Petite ligne de séparation
st.write("📢 **Aide tes frères à réussir avec Ratcom AI !**")

# Ton lien Streamlit (remplace par ton vrai lien)
mon_lien = "https://ratcom-ai.streamlit.app"
# Le message que les gens vont envoyer
message_whatsapp = f"Regarde cette IA 100% Camerounaise ! Elle connaît Douala et le business au pays : {mon_lien}"

# Création du lien de partage
lien_partage = f"https://wa.me{message_whatsapp.replace(' ', '%20')}"

# Affichage du bouton
st.markdown(f"""
    <a href="{lien_partage}" target="_blank">
        <button style="
            background-color: #25D366;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
        ">
            🚀 PARTAGER SUR WHATSAPP
        </button>
    </a>
    """, unsafe_allow_html=True)
