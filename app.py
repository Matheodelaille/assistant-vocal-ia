import streamlit as st
import openai
import tempfile
import os
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import base64

# Configuration
st.set_page_config(page_title="Assistant Vocal IA", page_icon="🤖")

# Titre
st.title("🎤 Assistant Vocal Intelligent")
st.markdown("Parlez-moi et je vous répondrai !")

# Sidebar pour la configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Clé API OpenAI", type="password")
    if api_key:
        openai.api_key = api_key
        st.success("Clé API configurée!")
    else:
        st.warning("Entrez votre clé OpenAI API")
    
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("1. Enregistrez votre voix")
    st.markdown("2. L'IA transcrira et répondra")
    st.markdown("3. Écoutez la réponse")

# Initialisation de session
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Enregistrement audio
st.subheader("🎤 Enregistrez votre voix")
audio_bytes = audio_recorder(
    text="Cliquez pour enregistrer",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_name="microphone",
    icon_size="2x",
)

# Traitement de l'audio
if audio_bytes:
    # Sauvegarde temporaire de l'audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        audio_path = tmp_file.name
    
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Transcription en cours..."):
        try:
            # Transcription avec Whisper (API OpenAI)
            with open(audio_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            texte_utilisateur = transcript.text
            st.success(f"**Vous avez dit :** {texte_utilisateur}")
            
            # Ajout à l'historique
            st.session_state.messages.append({"role": "user", "content": texte_utilisateur})
            
            # Génération de la réponse
            with st.spinner("L'IA réfléchit..."):
                # Préparation du contexte
                messages_for_api = [
                    {"role": "system", "content": "Vous êtes un assistant vocal français, utile et courtois. Répondez de manière concise."}
                ]
                
                # Ajout des derniers messages pour le contexte
                for msg in st.session_state.messages[-4:]:  # Garde les 4 derniers messages
                    messages_for_api.append(msg)
                
                # Appel à GPT
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages_for_api,
                    max_tokens=200
                )
                
                reponse_ia = response.choices[0].message.content
                
                # Affichage de la réponse
                with st.chat_message("assistant"):
                    st.markdown(reponse_ia)
                
                # Ajout à l'historique
                st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
                
                # Synthèse vocale (gTTS - gratuit)
                with st.spinner("Génération de la voix..."):
                    tts = gTTS(text=reponse_ia, lang='fr')
                    audio_file_tts = "reponse.mp3"
                    tts.save(audio_file_tts)
                    
                    # Lecture automatique
                    audio_bytes_tts = open(audio_file_tts, "rb").read()
                    st.audio(audio_bytes_tts, format="audio/mp3")
                    
                    # Nettoyage
                    os.remove(audio_file_tts)
            
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists(audio_path):
                os.remove(audio_path)

# Instructions supplémentaires
st.markdown("---")
st.markdown("**Pour utiliser cette application:**")
st.markdown("1. Obtenez une clé API sur [platform.openai.com](https://platform.openai.com)")
st.markdown("2. Collez-la dans la sidebar")
st.markdown("3. Parlez en cliquant sur le microphone")
