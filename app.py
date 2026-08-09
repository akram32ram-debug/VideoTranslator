import streamlit as st
import moviepy.editor as mp
import os
import tempfile
import asyncio
import edge_tts

async def generate_tts(text, output_audio_path):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_audio_path)

st.title("🎥 Simple Video Tool")
st.write("Apna video upload karein!")

uploaded_file = st.file_uploader("Upload Video (MP4)", type=["mp4"])

if uploaded_file is not None:
    if st.button("Process Video"):
        with st.spinner("Processing..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                temp_video.write(uploaded_file.read())
                video_path = temp_video.name

            audio_path = "temp_audio.wav"
            output_video_path = "final_output.mp4"

            # Video se audio alag karna
            video = mp.VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, logger=None)

            st.success("Video processed successfully!")
            st.video(video_path)
