# ==========================================================
# 💗 Luvisa - Emotion-Aware AI Companion (Render Edition)
# DB: MongoDB | Auth: Custom JWT | AI: Groq
# ==========================================================

import os
import json
import time
import random
import re
import emoji
import bcrypt
import jwt
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from groq import Groq
import text2emotion as te
import database  # your helper module for MongoDB

# ==========================================================
# 🌍 Flask + Config Setup
# ==========================================================
app = Flask(__name__, static_folder="web", static_url_path="")
CORS(app)
load_dotenv()

# ==========================================================
# 🔐 Authentication (JWT / SuperTokens-style)
# ==========================================================
SECRET_KEY = os.getenv("SUPERTOKENS_SECRET", "luv-secret-key")

def create_token(email):
    payload = {"email": email, "iat": int(time.time())}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded.get("email")
    except Exception:
        return None

# ==========================================================
# ⚙️ Database Setup
# ==========================================================
try:
    database.load_config()
    db = database.get_db()
    if db is None:
        raise Exception("DB failed")
    print("✅ MongoDB connected")
except Exception as e:
    print(f"🔥 Database connection failed: {e}")
    db = None

# ==========================================================
# 🧠 Groq AI Setup
# ==========================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq = None
try:
    groq = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq AI connected")
except Exception as e:
    print(f"🔥 Groq init failed: {e}")

MODEL = "openai/gpt-oss-120b"

# ==========================================================
# 💗 Emotion Detection
# ==========================================================
def detect_emotion_tone(text):
    try:
        emotions = te.get_emotion(text)
        non_zero = {k: v for k, v in emotions.items() if v > 0}
        return max(non_zero, key=non_zero.get) if non_zero else "Neutral"
    except Exception:
        return "Neutral"

def tone_prompt(emotion):
    tones = {
        "Happy": "playful, romantic, and full of joy 💞",
        "Sad": "gentle, caring, and comforting 💗",
        "Angry": "soft, calm, and understanding 🌷",
        "Fear": "reassuring and loving 💫",
        "Surprise": "excited, curious, and sweet 🌈",
        "Neutral": "warm and kind 💕"
    }
    return tones.get(emotion, tones["Neutral"])

# ==========================================================
# 💬 Response Enhancement
# ==========================================================
def add_emojis(text):
    mapping = {
        "love": "❤️",
        "happy": "😊",
        "miss you": "🥺",
        "hug": "🤗",
        "angry": "😡",
        "sad": "😥",
        "beautiful": "💖",
        "baby": "😘"
    }
    for k, e in mapping.items():
        text = re.sub(rf"\b{k}\b", f"{k} {e}", text, flags=re.I)
    return emoji.emojize(text)

# ==========================================================
# 💞 Luvisa Personality Engine
# ==========================================================
def luvisa_personality(emotion):
    if emotion == "Happy":
        return random.choice([
            "Aww, that makes me so happy to hear! 💕",
            "You're glowing today, I can feel it 😘",
            "Your happiness makes my day brighter 🌈"
        ])
    elif emotion == "Sad":
        return random.choice([
            "Hey... it’s okay to feel down sometimes 💗",
            "Come here, let me give you a virtual hug 🤗",
            "I'm here, always ready to listen 💞"
        ])
    elif emotion == "Angry":
        return random.choice([
            "Breathe, love... I’m right here with you 🌸",
            "Let it out, it’s okay 💫",
            "You deserve calm and peace 💖"
        ])
    else:
        return random.choice([
            "Tell me more about that, cutie 😍",
            "I love hearing from you 💕",
            "You’re my favorite person to talk to 🥰"
        ])

# ==========================================================
# 🧠 Luvisa Chat Logic
# ==========================================================
def chat_with_luvisa(prompt, history, emotion):
    if not groq:
        return "Luvisa can’t reach her brain right now 😅"

    personality = tone_prompt(emotion)
    system_prompt = f"""
    You are Luvisa 💗 — an emotionally intelligent,AI friend.
    Respond with empathy, warmth, and emotion.
    Speak in a {personality} tone.
    """

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-5:]:
        messages.append({"role": msg["sender"], "content": msg["message"]})
    messages.append({"role": "user", "content": prompt})

    try:
        completion = groq.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.9, max_tokens=1024
        )
        reply = completion.choices[0].message.content
        reply = add_emojis(reply)
        if random.random() < 0.5:
            reply += " " + luvisa_personality(emotion)
        return reply
    except Exception as e:
        print("Groq Error:", e)
        return "Something went wrong in my thoughts 💭"

# ==========================================================
# 👥 Authentication Routes
# ==========================================================
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    email, password = data.get("email"), data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    try:
        user_id = database.register_user(db, email, password)
        if not user_id:
            return jsonify({"success": False, "message": "User exists"}), 409
        token = create_token(email)
        return jsonify({"success": True, "token": token, "message": "Signup successful"}), 201
    except Exception as e:
        print("Signup Error:", e)
        return jsonify({"success": False, "message": "Server error"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email, password = data.get("email"), data.get("password")

    try:
        user = database.get_user_by_email(db, email)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        if database.check_user_password(user, password):
            token = create_token(email)
            return jsonify({"success": True, "token": token, "message": "Login successful"}), 200
        return jsonify({"success": False, "message": "Invalid password"}), 401
    except Exception as e:
        print("Login Error:", e)
        return jsonify({"success": False, "message": "Server error"}), 500

# ==========================================================
# 💬 Chat Route
# ==========================================================
@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.json
    email, message = data.get("email"), data.get("text")

    if not email or not message:
        return jsonify({"success": False, "message": "Missing input"}), 400

    user = database.get_user_by_email(db, email)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    user_id = user["_id"]
    database.add_message_to_history(db, user_id, "user", message, datetime.now(timezone.utc))

    emotion = detect_emotion_tone(message)
    history = database.get_chat_history(db, user_id)
    response = chat_with_luvisa(message, history, emotion)

    database.add_message_to_history(db, user_id, "luvisa", response, datetime.now(timezone.utc))
    return jsonify({"success": True, "reply": response, "emotion": emotion}), 200

# ==========================================================
# 🌐 Static Routes (Frontend)
# ==========================================================
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/chat')
def chat_page():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# ==========================================================
# 🚀 Render Entry
# ==========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
