import os
import json
import random
import datetime
import pyttsx3
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import AzureOpenAI

# Load .env variables
load_dotenv()

# Initialize Azure OpenAI GPT-4o
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

deployment_name = os.getenv("AZURE_DEPLOYMENT")

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# 🧠 Mood Detection Function
def detect_mood(text):
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    if compound >= 0.5:
        return "happy"
    elif compound >= 0.1:
        return "content"
    elif compound > -0.1:
        return "neutral"
    elif compound > -0.5:
        return "stressed"
    else:
        return "low"

# 💬 GPT-based Suggestion Generator
def get_suggestion(mood):
    prompt = f"My mood is '{mood}'. Give me a short, kind, and calming self-care suggestion."
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a warm and empathetic mental health companion."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Suggestion unavailable: {e})"

# 📓 GPT-based Journal Entry Generator
def generate_journal_entry(user_input, mood):
    prompt = (
        f"The user said: '{user_input}' and is feeling '{mood}'. "
        "Generate a reflective, comforting, and positive journal entry in first person tone."
    )
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You help generate uplifting journal reflections for mental clarity."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Journal unavailable: {e})"

# 📦 Mood & Journal Logger
def log_mood(mood, text, name="default"):
    os.makedirs("data", exist_ok=True)
    filename = f"data/{name.lower()}_mood_logs.json"
    logs = []

    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mood": mood,
        "entry": text
    })

    with open(filename, "w") as f:
        json.dump(logs, f, indent=2)

# 📊 Mood Trend Graph
def show_mood_trend(name="default"):
    filename = f"data/{name.lower()}_mood_logs.json"
    if not os.path.exists(filename):
        return

    with open(filename, "r") as f:
        logs = json.load(f)

    mood_score_map = {"low": 1, "stressed": 2, "neutral": 3, "content": 4, "happy": 5}
    dates = [entry["date"] for entry in logs[-7:]]
    scores = [mood_score_map.get(entry["mood"], 3) for entry in logs[-7:]]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, scores, marker='o', linestyle='-', color='#6a0572')
    plt.xticks(rotation=45, ha='right')
    plt.yticks([1, 2, 3, 4, 5], ["Low", "Stressed", "Neutral", "Content", "Happy"])
    plt.title("Your Mood Trend (Recent 7 entries)", fontsize=12)
    plt.tight_layout()
    plt.grid(True)
    st.pyplot(plt)

# 🚨 Alert System for 3 Low/Stressed Moods
def check_alert(name="default"):
    filename = f"data/{name.lower()}_mood_logs.json"
    if not os.path.exists(filename):
        return False

    with open(filename, "r") as f:
        logs = json.load(f)

    recent = logs[-3:]
    return all(entry["mood"] in ["low", "stressed"] for entry in recent)

# 🗣️ Text-to-Speech Output
def speak(message):
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception:
        pass
