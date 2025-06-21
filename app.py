import streamlit as st
from utils import detect_mood, get_suggestion, log_mood, check_alert, generate_journal_entry, show_mood_trend, speak
import random

st.set_page_config(page_title="Mindsy – Emotional AI", layout="wide", page_icon="🧠")

# ✨ Custom Styling
st.markdown("""
<style>
    @keyframes floatIn {
        0% { transform: translateY(-10px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    .stApp {
        background: linear-gradient(to right, #e0c3fc, #8ec5fc);
        padding: 2rem;
        font-family: 'Segoe UI', sans-serif;
        color: #222;
        animation: floatIn 1s ease-in-out;
    }
    textarea, .stTextInput input {
        border: 2px solid #c3aed6 !important;
        border-radius: 10px !important;
        background-color: #ffffff !important;
        color: #111111 !important;
        font-size: 16px !important;
        transition: all 0.3s ease-in-out;
    }
    .stTextInput input:focus, textarea:focus {
        box-shadow: 0 0 10px #8ec5fc;
    }
    .stButton button {
        background-color: #6a0572 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem;
        transition: all 0.4s ease-in-out;
        box-shadow: 0 0 0px transparent;
    }
    .stButton button:hover {
        background-color: #9d0191 !important;
        box-shadow: 0 0 12px #fff, 0 0 18px #fbc7ff;
        transform: scale(1.03);
    }
    .floating-pet {
        position: absolute;
        top: 10px;
        right: 20px;
        animation: floatIn 2s ease-in-out infinite alternate;
    }
</style>
""", unsafe_allow_html=True)

# 🐶 Floating Pet Avatar
st.markdown("""
<div class="floating-pet">
    <img src="https://cdn-icons-png.flaticon.com/512/616/616408.png" width="60">
</div>
""", unsafe_allow_html=True)

# 🌈 Title
st.title("🌈 Mindsy – Your AI Mood Companion")

# 👤 Ask for user name
if "name" not in st.session_state or not st.session_state.name:
    st.session_state.name = st.text_input("👋 Before we begin, what's your name?")

# 🎧 Calming Music Option
with st.expander("🎧 Need calming background music?"):
    st.audio("https://www.bensound.com/bensound-music/bensound-slowmotion.mp3", format='audio/mp3')

# 🎉 Personalized welcome
if st.session_state.name:
    st.markdown(f"### Welcome, **{st.session_state.name}** 💚 Mindsy is here for you today.")

    if st.button("💖 Daily Affirmation"):
        affirmation = random.choice([
            "You are stronger than you feel.",
            "Peace begins with one deep breath.",
            "You’re not alone — Mindsy is here. 💚",
            "Your feelings are valid.",
            "This moment is yours. Breathe into it."
        ])
        st.success(f"🌟 {affirmation}")
        speak(affirmation)

    # 💬 Mood Input
    st.markdown("### 💬 How are you feeling right now?")
    user_input = st.text_area("Write how you're feeling in a sentence or two", "", height=180)

    if "mood" not in st.session_state:
        st.session_state.mood = ""
    if "suggestion" not in st.session_state:
        st.session_state.suggestion = ""
    if "example_journal" not in st.session_state:
        st.session_state.example_journal = ""

    # 🧠 Analyze mood
    if st.button("🧠 Analyze My Feelings"):
        if not user_input.strip():
            st.warning("Please tell Mindsy how you're feeling 🧠💬")
        else:
            mood = detect_mood(user_input)
            suggestion = get_suggestion(mood)
            st.session_state.mood = mood
            st.session_state.suggestion = suggestion
            log_mood(mood, user_input, st.session_state.name)

    # 🧾 Display Results
    if st.session_state.mood:
        st.success(f"🧠 Mindsy thinks you're feeling **{st.session_state.mood.upper()}**, {st.session_state.name} 🌸")
        st.markdown(f"**🗣️ Mindsy says:** *{st.session_state.suggestion}*")

        if st.button("🔊 Let Mindsy speak this"):
            speak(st.session_state.suggestion)

        if check_alert(st.session_state.name):
            st.error("🚨 You've felt low/stressed 3 times in a row. Please consider reaching out to someone 💛")

        st.markdown("### 📓 Want to journal your thoughts?")

        if "journal_entry" not in st.session_state:
            st.session_state.journal_entry = ""

        st.session_state.journal_entry = st.text_area(
            "Write from the heart 💖", value=st.session_state.journal_entry,
            key="journal_box", height=200
        )

        if st.button("📝 Save My Journal Entry"):
            log_mood(st.session_state.mood, st.session_state.journal_entry, st.session_state.name)
            st.success("✅ Your journal has been saved successfully!")

        if st.button("💡 Inspire Me With a Journal Entry"):
            st.session_state.example_journal = generate_journal_entry(user_input, st.session_state.mood)

        if st.session_state.example_journal:
            st.info("Here’s a journal entry you can reflect on or rewrite:")
            st.code(st.session_state.example_journal)

        st.markdown("### 📊 Your Mood Trend Over Time")
        show_mood_trend(st.session_state.name)
