import streamlit as st
import openai
import tempfile
import os
from gtts import gTTS
import base64

# Configuration
st.set_page_config(page_title="Assistant Vocal IA", page_icon="🤖")

# Titre
st.title("🎤 Assistant Vocal Intelligent")
st.markdown("### Version Simplifiée - Pas besoin d'enregistrement audio pour commencer!")

# Instructions claires
st.info("""
**Mode d'emploi :**
1. Entrez votre clé OpenAI API ci-dessous
2. Tapez votre message dans la zone de texte
3. Cliquez sur "Envoyer"
4. Écoutez la réponse audio!
""")

# Sidebar pour la configuration
with st.sidebar:
    st.header("🔑 Configuration")
    
    # Option 1 : Clé API directe
    api_key = st.text_input("Clé API OpenAI", type="password", 
                          help="Obtenez une clé sur https://platform.openai.com/api-keys")
    
    # Option 2 : Fichier .env
    st.markdown("---")
    st.subheader("OU utilisez un fichier .env")
    st.code("""
# Créez un fichier .env avec :
OPENAI_API_KEY=votre_clé_ici
""")
    
    if os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
        if os.getenv("OPENAI_API_KEY"):
            api_key = os.getenv("OPENAI_API_KEY")
            st.success("Clé chargée depuis .env!")
    
    if api_key:
        openai.api_key = api_key
        st.success("✅ Clé API configurée!")
    else:
        st.warning("⚠️ Entrez votre clé API pour continuer")
    
    # Modèle sélection
    st.markdown("---")
    model_choice = st.selectbox(
        "Modèle",
        ["gpt-3.5-turbo", "gpt-4"],
        index=0
    )
    
    # Bouton test
    if st.button("🔍 Tester la connexion API"):
        try:
            openai.models.list()
            st.success("Connexion API réussie!")
        except:
            st.error("Échec de connexion. Vérifiez votre clé.")

# Initialisation de l'historique
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Vous êtes un assistant vocal français utile et courtois. Répondez de manière concise et claire."}
    ]

# Affichage de l'historique
st.subheader("💬 Conversation")
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] != "system":  # On n'affiche pas le message système
            with st.chat_message(message["role"]):
                st.write(message["content"])

# Zone d'entrée utilisateur
st.subheader("✍️ Votre message")

# Option texte (pour commencer)
user_input = st.text_area("Tapez votre message ici:", 
                         height=100,
                         placeholder="Ex: Bonjour! Peux-tu m'expliquer comment fonctionne l'IA?")

# Boutons d'action
col1, col2, col3 = st.columns(3)

with col1:
    send_button = st.button("🚀 Envoyer", type="primary", use_container_width=True)

with col2:
    if st.button("🧹 Effacer l'historique", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "Vous êtes un assistant vocal français utile et courtois."}
        ]
        st.rerun()

with col3:
    if st.button("🎤 Version Audio", use_container_width=True, disabled=True):
        st.info("Version audio à venir! Pour l'instant, utilisez le texte.")

# Traitement du message
if send_button and user_input and api_key:
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Affichage immédiat
    with st.chat_message("user"):
        st.write(user_input)
    
    # Génération de la réponse
    with st.chat_message("assistant"):
        with st.spinner("🤖 L'IA réfléchit..."):
            try:
                response = openai.chat.completions.create(
                    model=model_choice,
                    messages=st.session_state.messages,
                    max_tokens=300,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
                # Affichage texte
                st.write(ai_response)
                
                # Ajout à l'historique
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # Synthèse vocale
                with st.spinner("🔊 Génération de la voix..."):
                    try:
                        tts = gTTS(text=ai_response, lang='fr', slow=False)
                        
                        # Sauvegarde temporaire
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(temp_file.name)
                        
                        # Lecture audio
                        audio_bytes = open(temp_file.name, "rb").read()
                        audio_base64 = base64.b64encode(audio_bytes).decode()
                        
                        # HTML pour l'audio
                        audio_html = f"""
                        <audio controls autoplay style="width: 100%; margin-top: 10px;">
                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                            Votre navigateur ne supporte pas l'audio.
                        </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                        
                        # Nettoyage
                        os.unlink(temp_file.name)
                        
                        st.success("✅ Réponse audio générée!")
                        
                    except Exception as e:
                        st.warning(f"⚠️ Audio non disponible: {str(e)}")
                        st.info("Réponse texte seulement.")
                
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                st.info("Vérifiez votre clé API et votre connexion internet.")

elif send_button and not api_key:
    st.error("❌ Veuillez entrer votre clé API OpenAI dans la sidebar!")
elif send_button and not user_input:
    st.warning("⚠️ Veuillez taper un message!")

# Section d'aide
with st.expander("❓ Aide et Dépannage"):
    st.markdown("""
    **Problèmes courants :**
    
    1. **Clé API invalide** : Obtenez-en une sur [platform.openai.com](https://platform.openai.com)
    2. **Pas d'audio** : Assurez-vous que votre navigateur autorise l'audio
    3. **Erreur de connexion** : Vérifiez votre connexion internet
    
    **Prochaines étapes :**
    - Ajout de l'enregistrement vocal
    - Mémoire entre les sessions
    - Interface plus avancée
    
    **Pour tester sans clé API :**
    ```python
    # Simulation de réponse
    st.write("Bonjour! Ceci est une simulation.")
    ```
    """)

# Pied de page
st.markdown("---")
st.caption("Développé avec ❤️ | Assistant Vocal IA v1.0 | [GitHub](https://github.com/Matheodelaille/assistant-vocal-ia)")
