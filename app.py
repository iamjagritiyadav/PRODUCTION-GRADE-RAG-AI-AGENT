import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Page Setup
st.set_page_config(
    page_title="Pulse RAG",
    page_icon="⚡",
    layout="wide"
)

# Gemini-Inspired Custom CSS
st.markdown("""
    <style>
    /* Dark Theme background */
    .stApp {
        background-color: #131314;
    }
    
    /* Gradient Text for Pulse RAG */
    .gemini-title {
        background: linear_gradient(to right, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 600;
        font-family: 'Google Sans', sans-serif;
    }

    /* Chat containers */
    .stChatMessage {
        background-color: #1e1f20 !important;
        border-radius: 20px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
    }

    /* Input Box styling */
    .stChatInputContainer {
        padding-bottom: 2rem;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20;
        border-right: 1px solid #333;
    }
    
    .status-active {
        color: #00e676;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# App Branding
st.markdown('<h1 class="gemini-title">⚡ Pulse RAG</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #8e918f; font-size: 1.2rem; margin-top: -15px;'>Your event-driven intelligence agent</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_wordmark_light_6021c7d777e45.svg", width=150)
    st.divider()
    
    st.subheader("📚 Knowledge Base")
    uploaded = st.file_uploader("Upload document (PDF)", type=["pdf"])
    
    if uploaded and st.button("Index to Pulse"):
        with st.status("Absorbing knowledge...", expanded=False):
            # Same logic as before
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            file_path = uploads_dir / uploaded.name
            file_path.write_bytes(uploaded.getbuffer())
            
            # Send Inngest event
            client = inngest.Inngest(app_id="pulse_rag", is_production=False)
            asyncio.run(client.send(inngest.Event(
                name="pulse/ingest_pdf",
                data={"pdf_path": str(file_path.resolve()), "source_id": uploaded.name}
            )))
            st.success(f"'{uploaded.name}' Pulse mein add ho gaya!")

    st.divider()
    st.markdown("System Status: <span class='status-active'>Pulse Live</span>", unsafe_allow_html=True)

# Inngest Polling Helper
def wait_for_pulse_output(event_id: str):
    url = f"http://127.0.0.1:8288/api/events/{event_id}/runs"
    start_time = time.time()
    while time.time() - start_time < 60:
        try:
            r = requests.get(url, timeout=2).json()
            if r and r[0]['status'] in ("Completed", "Succeeded"):
                return r[0].get("output")
        except: pass
        time.sleep(1)
    return None

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input (Gemini style)
if prompt := st.chat_input("Ask Pulse anything..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Trigger AI Pulse
    with st.chat_message("assistant"):
        with st.spinner("Pulse is thinking..."):
            client = inngest.Inngest(app_id="pulse_rag", is_production=False)
            event_id = asyncio.run(client.send(inngest.Event(
                name="pulse/query",
                data={"question": prompt, "top_k": 5}
            )))
            
            output = wait_for_pulse_output(event_id[0])
            
            if output:
                response = output.get("answer", "Maaf kijiye, main iska jawab nahi dhoond paya.")
                st.markdown(response)
                
                if output.get("sources"):
                    st.caption(f"Sources: {', '.join(output['sources'])}")
                
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("Backend response nahi mila. Inngest dev server check karein.")
