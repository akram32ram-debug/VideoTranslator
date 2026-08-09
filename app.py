import streamlit as st
import moviepy.editor as mp
import whisper
import os
import tempfile
import asyncio
import edge_tts
from deep_translator import GoogleTranslator

# --- Page Configuration & Google Search Console Verification ---
st.set_page_config(
    page_title="TranslateAI Pro - Multi-Language Dubbing",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Search Console Meta Tag Integrated
st.markdown('<meta name="google-site-verification" content="O8FzJ2HI4_XeHf3nD061ujpOB2aWw3kpaTI6BSCh3PA" />', unsafe_allow_html=True)

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

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/video-interpreter.png", width=70)
    st.title("TranslateAI Pro")
    st.caption("Perfect Multi-Language Dubbing")
    st.divider()
    st.success("✅ SEO Verified & Active")
    st.divider()
    st.caption("© 2026 TranslateAI Inc.")

# --- Header ---
st.title("🎬 Global AI Video Dubbing Engine")
st.markdown("##### Upload your video and perfectly dub it into any language worldwide!")
st.write("")

# --- Language & Voice Settings ---
SUPPORTED_LANGUAGES = {
    "English (US)": {"code": "en", "voice": "en-US-AriaNeural"},
    "English (UK)": {"code": "en", "voice": "en-GB-SoniaNeural"},
    "Spanish (Spain)": {"code": "es", "voice": "es-ES-ElviraNeural"},
    "French (France)": {"code": "fr", "voice": "fr-FR-DeniseNeural"},
    "German (Germany)": {"code": "de", "voice": "de-DE-AmalaNeural"},
    "Japanese (Japan)": {"code": "ja", "voice": "ja-JP-NanamiNeural"},
    "Arabic (Saudi)": {"code": "ar", "voice": "ar-SA-ZariyahNeural"},
    "Hindi (India)": {"code": "hi", "voice": "hi-IN-SwaraNeural"}
}

# --- Model Loading ---
@st.cache_resource
def load_model():
    return whisper.load_model("base")

async def generate_tts(text, output_audio_path, voice_name):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_audio_path)

# --- App Layout ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.subheader("📥 1. Upload & Setup")
    uploaded_file = st.file_uploader("Choose an MP4 File", type=["mp4", "mov"])
    
    selected_language = st.selectbox(
        "🌍 Choose Dubbing Language:",
        list(SUPPORTED_LANGUAGES.keys())
    )
    
    st.info("💡 Note: AI वीडियो की आवाज़ सुनकर उसे चुनिंदा भाषा में डब करेगा।")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.subheader("⚡ 2. Processing & Output")
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("✨ Start Perfect Dubbing"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                    temp_video.write(uploaded_file.read())
                    video_path = temp_video.name

                audio_path = "temp_audio.wav"
                new_audio_path = "new_dubbed_audio.mp3"
                output_video_path = "final_dubbed_video.mp4"

                # Step 1: Extract Audio
                status_text.text("⚙️ Step 1/4: Extracting Audio...")
                progress_bar.progress(20)
                video = mp.VideoFileClip(video_path)
                video.audio.write_audiofile(audio_path, logger=None)

                # Step 2: Transcription
                status_text.text("🧠 Step 2/4: Listening to Audio (Whisper)...")
                progress_bar.progress(45)
                model = load_model()
                result = model.transcribe(audio_path, fp16=False)
                original_text = result.get("text", "")

                # Step 3: Translation
                status_text.text(f"🌐 Step 3/4: Translating to {selected_language}...")
                progress_bar.progress(70)
                target_code = SUPPORTED_LANGUAGES[selected_language]["code"]
                target_voice = SUPPORTED_LANGUAGES[selected_language]["voice"]
                
                translator = GoogleTranslator(source='auto', target=target_code)
                translated_text = translator.translate(original_text)

                # Step 4: Voice Generation & Merging
                status_text.text("🎙️ Step 4/4: Generating AI Voice & Rendering...")
                progress_bar.progress(90)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate_tts(translated_text, new_audio_path, target_voice))

                new_audio = mp.AudioFileClip(new_audio_path)
                final_video = video.set_audio(new_audio)
                final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", logger=None)

                progress_bar.progress(100)
                status_text.text("✅ Perfect Dubbing Completed!")
                st.success("🎉 Your professional video is ready!")

                # Play & Download
                st.video(output_video_path)
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label=f"📥 Download {selected_language} Video",
                        data=file,
                        file_name=f"dubbed_{target_code}.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"Execution Error: {e}")
    else:
        st.info("👆 Please upload an MP4 video from the left panel.")
        
    st.markdown("</div>", unsafe_allow_html=True)
