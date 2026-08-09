import streamlit as st
import moviepy.editor as mp
import whisper
import os
import tempfile
import asyncio
import edge_tts
from deep_translator import GoogleTranslator

# --- Page Configuration ---
st.set_page_config(
    page_title="TranslateAI Pro - Next-Gen Video Translator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (SaaS Look) ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0px 4px 15px rgba(168, 85, 247, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 20px rgba(168, 85, 247, 0.6);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar (Monetization & Plans) ---
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/video-interpreter.png", width=70)
    st.title("TranslateAI Pro")
    st.caption("AI-Powered Video Dubbing")
    st.divider()
    
    st.subheader("👑 Upgrade to Pro")
    st.markdown("""
    - ⚡ **10x Faster Translation**
    - 💎 **Unlimited Video Length**
    - 🎙️ **Natural Voice Cloning**
    - 🎥 **4K Video Export**
    """)
    if st.button("🚀 Unlock Pro Plan ($9/mo)"):
        st.balloons()
        st.info("Monetization Link / Payment Gateway integration ready!")

    st.divider()
    st.caption("© 2026 TranslateAI Inc. All rights reserved.")

# --- Header ---
st.title("🎬 AI Video Translator & Dubbing Engine")
st.markdown("##### Upload your Hindi video, and our AI will automatically transcribe, translate, and dub it into natural English voice!")

st.write("")

# --- Model Loading ---
@st.cache_resource
def load_model():
    return whisper.load_model("tiny")

async def generate_english_tts(text, output_audio_path, voice_name="en-US-AriaNeural"):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_audio_path)

# --- App Layout (Two Columns) ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.subheader("📥 1. Upload Video Source")
    uploaded_file = st.file_uploader("Choose an MP4 File", type=["mp4", "mov"])
    
    selected_voice = st.selectbox(
        "🎙️ Choose English Voice:",
        ["Aria (Female - US)", "Guy (Male - US)", "Sonia (Female - UK)", "Ryan (Male - UK)"]
    )
    voice_codes = {
        "Aria (Female - US)": "en-US-AriaNeural",
        "Guy (Male - US)": "en-US-GuyNeural",
        "Sonia (Female - UK)": "en-GB-SoniaNeural",
        "Ryan (Male - UK)": "en-GB-RyanNeural"
    }

    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.subheader("⚡ 2. Processing & Output")
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("✨ Auto Translate & Dub Video"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Setup Temp Files
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                    temp_video.write(uploaded_file.read())
                    video_path = temp_video.name

                audio_path = "temp_audio.wav"
                new_audio_path = "new_english_audio.mp3"
                output_video_path = "final_translated_video.mp4"

                # Step 1: Extract Audio
                status_text.text("⚙️ Step 1/4: Extracting Audio Track...")
                progress_bar.progress(25)
                video = mp.VideoFileClip(video_path)
                video.audio.write_audiofile(audio_path, logger=None)

                # Step 2: Speech to Text (Whisper AI)
                status_text.text("🧠 Step 2/4: Transcribing Hindi Audio with AI...")
                progress_bar.progress(50)
                model = load_model()
                result = model.transcribe(audio_path, fp16=False)
                hindi_text = result.get("text", "")

                # Step 3: Translate Text
                status_text.text("🌐 Step 3/4: Translating to Natural English...")
                progress_bar.progress(75)
                translator = GoogleTranslator(source='auto', target='en')
                english_text = translator.translate(hindi_text)

                # Step 4: Generate Voice & Merge Video
                status_text.text("🎙️ Step 4/4: Generating AI Voice & Rendering Video...")
                progress_bar.progress(90)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate_english_tts(english_text, new_audio_path, voice_codes[selected_voice]))

                new_audio = mp.AudioFileClip(new_audio_path)
                final_video = video.set_audio(new_audio)
                final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", logger=None)

                progress_bar.progress(100)
                status_text.text("✅ Dubbing Completed Successfully!")
                st.success("🎉 Your translated video is ready!")

                # Final Video Output & Download
                st.video(output_video_path)
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Translated Video (HD)",
                        data=file,
                        file_name="dubbed_video.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"Execution Error: {e}")
    else:
        st.info("👆 Please upload an MP4 video from the left panel to begin translation.")
        
    st.markdown("</div>", unsafe_allow_html=True)
