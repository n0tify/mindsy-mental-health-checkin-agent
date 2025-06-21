import json
import os
import re
from datetime import date, datetime
import matplotlib.pyplot as plt
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import AzureOpenAI
import pyttsx3

# 🧠 GPT-4o Client Setup (Azure)
client = AzureOpenAI(
    api_key="8WxLaoodYxa7XSK2rCiWuP3nqwWUShSUVd5FrjEYSqqROfIwc0qzJQQJ99BFAC77bzfXJ3w3AAABACOGweqQ",
    api_version="2024-12-01-preview",
    azure_endpoint="https://mindcraft-kapidhwaj-openai-api-key.openai.azure.com/"
)

# 🔒 Sanitize username for safe filenames
def sanitize_username(username):
    return re.sub(r'\W+', '', username.lower())

# 🔍 Mood detection using Vader
def detect_mood(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.5:
        return "happy"
    elif score > 0:
        return "neutral"
    elif score > -0.5:
        return "stressed"
    else:
        return "low"

# 💡 Get supportive suggestion from GPT
def get_suggestion(mood):
    try:
        response = client.chat.completions.create(
            model="mindcraft-gpt4o",
            messages=[
                {"role": "system", "content": "You are a helpful, kind mental health assistant."},
                {"role": "user", "content": f"Give a short comforting suggestion for someone feeling {mood}."}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Suggestion unavailable: {str(e)})"

# 📘 Generate reflective journal
def generate_journal_entry(user_input, mood):
    try:
        response = client.chat.completions.create(
            model="mindcraft-gpt4o",
            messages=[
                {"role": "system", "content": "You write short, warm, emotional journal reflections for users."},
                {"role": "user", "content": f"Write a gentle journal entry based on this input: '{user_input}', mood is {mood}."}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Today, I felt {mood}. I shared: {user_input}"

# 💾 Save mood and journal entry
def log_mood(mood, user_input, username):
    safe_user = sanitize_username(username)
    os.makedirs("data", exist_ok=True)  # ✅ Ensure folder exists

    filename = f"data/{safe_user}_mood_logs.json"
    entry = {
        "date": str(date.today()),
        "mood": mood,
        "input": user_input
    }

    try:
        with open(filename, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(entry)

    with open(filename, "w") as f:
        json.dump(logs, f, indent=2)

# 🚨 Check if user is repeatedly feeling low/stressed
def check_alert(username):
    safe_user = sanitize_username(username)
    filename = f"data/{safe_user}_mood_logs.json"

    try:
        with open(filename, "r") as f:
            logs = json.load(f)
        recent = logs[-3:]
        lows = [entry for entry in recent if entry["mood"] in ["low", "stressed"]]
        return len(lows) == 3
    except:
        return False

# 📊 Display mood trend
def show_mood_trend(username):
    safe_user = sanitize_username(username)
    filename = f"data/{safe_user}_mood_logs.json"

    try:
        with open(filename, "r") as f:
            data = json.load(f)
        if not data:
            st.info("No mood history yet.")
            return

        dates = [datetime.strptime(entry["date"], "%Y-%m-%d") for entry in data]
        mood_map = {"low": 1, "stressed": 2, "neutral": 3, "happy": 4}
        mood_levels = [mood_map.get(entry["mood"], 3) for entry in data]
        labels = {1: "😞 Low", 2: "😰 Stressed", 3: "😐 Neutral", 4: "😊 Happy"}

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(dates, mood_levels, marker='o', linestyle='-', color="#6a0572")
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels([labels[i] for i in [1, 2, 3, 4]])
        ax.set_title(f"Mood Trend for {username.title()}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Mood")
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)

    except:
        st.warning("⚠️ Could not display mood chart. Try journaling first.")

# 🔊 Text-to-speech
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except:
        st.warning("🗣️ Text-to-speech not supported on this system.")
