import streamlit as st
import moviepy.editor as mp
import whisper
import os
import tempfile
import asyncio
import edge_tts
from deep_translator import GoogleTranslator

# AI मॉडल को लोड करना (हल्का 'tiny' मॉडल ताकि सर्वर हैंग न हो)
@st.cache_resource
def load_model():
    return whisper.load_model("tiny")

model = load_model()

# Edge TTS से English आवाज़ बनाने का फंक्शन
async def generate_english_tts(text, output_audio_path):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_audio_path)

st.title("🎥 Auto Hindi to English Video Translator")
st.write("अपना हिंदी वीडियो अपलोड करें, AI खुद उसकी आवाज़ सुनकर इंग्लिश में ट्रांसलेट करेगा!")

# File uploader
uploaded_file = st.file_uploader("Upload Hindi Video (MP4)", type=["mp4"])

if uploaded_file is not None:
    if st.button("Auto Translate & Get Download Button"):
        with st.spinner("AI वीडियो की आवाज़ सुन रहा है... कृपया इंतज़ार करें।"):
            try:
                # 1. वीडियो को टेम्परेरी सेव करना
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                    temp_video.write(uploaded_file.read())
                    video_path = temp_video.name

                audio_path = "temp_audio.wav"
                new_audio_path = "new_english_audio.mp3"
                output_video_path = "final_translated_video.mp4"

                # 2. वीडियो से ऑडियो निकालना
                st.info("Step 1: वीडियो से आवाज़ निकाली जा रही है...")
                video = mp.VideoFileClip(video_path)
                video.audio.write_audiofile(audio_path, logger=None)

                # 3. आवाज़ को टेक्स्ट में बदलना (AI Listening)
                st.info("Step 2: AI आवाज़ सुन कर टेक्स्ट लिख रहा है...")
                result = model.transcribe(audio_path, fp16=False) # fp16=False CPU के लिए सेफ है
                hindi_text = result["text"]
                st.write(f"**Original Text (AI ने सुना):** {hindi_text}")

                # 4. ट्रांसलेशन (Hindi to English)
                st.info("Step 3: टेक्स्ट को इंग्लिश में ट्रांसलेट किया जा रहा है...")
                translator = GoogleTranslator(source='auto', target='en')
                english_text = translator.translate(hindi_text)
                st.write(f"**Translated English Text:** {english_text}")

                # 5. नई इंग्लिश आवाज़ (TTS)
                st.info("Step 4: नई इंग्लिश आवाज़ बनाई जा रही है...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate_english_tts(english_text, new_audio_path))

                # 6. नई आवाज़ को वीडियो के साथ जोड़ना
                st.info("Step 5: नई आवाज़ को वीडियो में जोड़ा जा रहा है...")
                new_audio = mp.AudioFileClip(new_audio_path)
                final_video = video.set_audio(new_audio)
                final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", logger=None)

                st.success("🎉 वीडियो सफलतापूर्वक ट्रांसलेट हो गया है!")
                
                # 7. स्क्रीन पर वीडियो दिखाना
                st.video(output_video_path)

                # 8. Download Button
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Download English Translated Video",
                        data=file,
                        file_name="english_translated_video.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"Error आ गया: {e}")
