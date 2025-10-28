# # --- Imports ---
# import bcrypt
# import base64
# import os
# import time
# import random
# from datetime import datetime, timezone # Added timezone
# import emoji
# import re
# import json
# from dotenv import load_dotenv
# from groq import Groq
# import nltk
# #import text2emotion as te
# import firebase_admin
# from firebase_admin import credentials, auth
# from bson.objectid import ObjectId
# from database import get_db

# # --- UPDATED: Import send_from_directory ---
# from flask import Flask, request, jsonify, send_from_directory, Response
# from flask_cors import CORS

# STATIC_FOLDER = "web"  # Must be declared before Flask app
# app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
# CORS(app, resources={r"/api/*": {"origins": "*"}})
# # app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
# # CORS(app)

# # app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
# # CORS(app, resources={r"/api/*": {"origins": "https://luvisa-companion.vercel.app"}})

# import database # Your database module

# # --- Configuration & Setup ---
# # Tell Flask where to find static files (CSS, JS, images)
# # STATIC_FOLDER = 'web'

# # --- Initialize Flask App ---
# # app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
# # CORS(app)

# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     print("⚠️ Missing NLTK data. Please ensure it's preloaded locally.")
    
# # --- Firebase Initialization ---
# try:
#     firebase_key_base64 = os.getenv("FIREBASE_KEY_BASE64")

#     # --- Vercel (Production) ---
#     if firebase_key_base64:
#         # Decode the Base64 string into JSON
#         firebase_key_json = base64.b64decode(firebase_key_base64).decode('utf-8')
#         key_dict = json.loads(firebase_key_json)

#         cred = credentials.Certificate(key_dict)
#         # Check if Firebase app is already initialized to prevent error
#         if not firebase_admin._apps:
#             firebase_admin.initialize_app(cred)
#             print("✅ Firebase Admin SDK initialized successfully from ENV variable.")
#         else:
#             print("✅ Firebase Admin SDK already initialized.")

#     # --- Local Fallback ---
#     elif os.path.exists("serviceAccountKey.json"):
#         # Check if Firebase app is already initialized
#         if not firebase_admin._apps:
#             cred = credentials.Certificate("serviceAccountKey.json")
#             firebase_admin.initialize_app(cred)
#             print("✅ Firebase Admin SDK initialized successfully from local file.")
#         else:
#              print("✅ Firebase Admin SDK already initialized.")

#     else:
#         print("🔥 Firebase credentials not found (no ENV var or local file).")

# except Exception as e:
#     print(f"🔥 Firebase Admin SDK initialization failed: {e}")

# # --- Groq Client ---
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_MODEL = "openai/gpt-oss-120b" # Ensure this model name is correct/available
# groq = None
# try:
#     if not GROQ_API_KEY:
#         raise ValueError("GROQ_API_KEY not found in the local .env file.")
#     groq = Groq(api_key=GROQ_API_KEY)
#     print(f"✅ Groq client initialized successfully for {GROQ_MODEL}.")
# except Exception as e:
#     print(f"🔥 Groq client initialization failed: {e}")
#     groq = None

# # --- MongoDB Client Setup ---
# # In main.py, around line 99

# try:
#     database.load_config() # Loads .env file
#     db = database.get_db() # Connects to MongoDB
#     if db is None:
#         raise Exception("Database connection returned None.")
#     else:
#         # --- ADDED: Call setup_indexes ---
#         database.setup_indexes(db) # <-- COMMENT THIS LINE OUT
#         pass # Add pass to avoid an indentation error
#         # --- END ---

# except Exception as e:
#     print(f"🔥🔥🔥 FATAL: Could not connect to MongoDB or setup indexes: {e}")


# # --- Frontend Serving Routes ---

# @app.route('/')
# def serve_index():
#     return send_from_directory(STATIC_FOLDER, 'login.html')

# @app.route('/chat')
# def serve_chat():
#     return send_from_directory(STATIC_FOLDER, 'index.html')

# @app.route('/login')
# def serve_login():
#     return send_from_directory(STATIC_FOLDER, 'login.html')

# @app.route('/signup')
# def serve_signup():
#     return send_from_directory(STATIC_FOLDER, 'signup.html')

# @app.route('/profile')
# def serve_profile():
#     # Note: This route might become unnecessary if profile editing is fully integrated
#     # Keep it for now if profile.html is still used as a fallback or separate page
#     return send_from_directory(STATIC_FOLDER, 'profile.html')

# # --- Authentication Logic (Using MongoDB) ---

# @app.route('/api/signup', methods=['POST'])
# def signup_route():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503
    
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password: return jsonify({"success": False, "message": "Email and password required."}), 400
#     if not re.match(r"[^@]+@[^@]+\.[^@]+", email): return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

#     try:
#         user_id = database.register_user(db, email, password)
#         if user_id is None:
#             return jsonify({"success": False, "message": "This email is already registered."}), 409
#     except Exception as e:
#         print(f"Signup DB Error: {e}")
#         return jsonify({"success": False, "message": "Database error during signup."}), 500

#     # Try Firebase Auth
#     try:
#         if firebase_admin._apps:
#             auth.create_user(email=email)
#             print(f"Successfully created user {email} in Firebase Auth console.")
#         else:
#             print("Firebase not initialized, skipping Firebase user creation.")
#     except Exception as e:
#         if 'EMAIL_EXISTS' not in str(e):
#              print(f"Warning: Could not create user in Firebase Auth console: {e}")

#     return jsonify({"success": True, "message": "Signup successful"}), 201

# @app.route('/api/login', methods=['POST'])
# def login_route():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503

#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({"success": False, "message": "Email and password required."}), 400

#     try:
#         user_doc = database.get_user_by_email(db, email)
#         if not user_doc:
#             return jsonify({"success": False, "message": "User not found"}), 404

#         if database.check_user_password(user_doc, password):
#             return jsonify({"success": True, "message": "Login successful", "email": email}), 200
#         else:
#             return jsonify({"success": False, "message": "Invalid password"}), 401

#     except Exception as e:
#         print(f"Login DB Error: {e}")
#         return jsonify({"success": False, "message": "Error during login."}), 500

# @app.route('/api/auto_login_check', methods=['POST'])
# def auto_login_check_route():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503
    
#     data = request.json
#     email = data.get('email')

#     if not email:
#         return jsonify({"isValid": False}), 400

#     try:
#         user_doc = database.get_user_by_email(db, email)
#         is_valid = user_doc is not None
#         return jsonify({"isValid": is_valid}), 200
#     except Exception as e:
#         print(f"Auto Login Check DB Error: {e}")
#         return jsonify({"isValid": False, "message": "Error checking user."}), 500

# # --- Profile Management (Using MongoDB) ---

# @app.route('/api/profile', methods=['GET'])
# def get_user_profile_route():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503

#     email = request.args.get('email')
#     if not email: return jsonify({"success": False, "message": "Email query parameter required."}), 400

#     try:
#         user_doc = database.get_user_by_email(db, email)
#         if not user_doc:
#             return jsonify({"success": False, "message": "User not found"}), 404

#         profile = user_doc.get('profile', {})
#         user_id_str = str(user_doc.get('_id'))
        
#         has_avatar = profile.get('profile_pic') and profile['profile_pic'].get('data')
#         avatar_url = f"/api/avatar/{user_id_str}" if has_avatar else None

#         profile_data = {
#             "email": user_doc.get('email'),
#             "display_name": profile.get('display_name', email.split('@')[0]),
#             "avatar": avatar_url,
#             "status": profile.get('bio', "Hey there! I’m using Luvisa 💗")
#         }
#         return jsonify({"success": True, "profile": profile_data}), 200

#     except Exception as e:
#         print(f"Get Profile DB Error: {e}")
#         return jsonify({"success": False, "message": "Error fetching profile."}), 500

# @app.route('/api/luvisa_profile', methods=['GET'])
# def get_luvisa_profile_route():
#     profile_data = {
#         "email": "luvisa@ai.com",
#         "display_name": "Luvisa 💗",
#         "avatar": "/avatars/luvisa_avatar.png",
#         "status": "Thinking of you... 💭"
#     }
#     return jsonify({"success": True, "profile": profile_data}), 200

# @app.route('/api/avatar/<user_id>')
# def serve_user_avatar(user_id):
#     if db is None: return "Database connection error.", 503

#     try:
#         user_doc = database.get_user_by_id(db, user_id)
#         if user_doc and user_doc.get('profile', {}).get('profile_pic', {}).get('data'):
#             pic_data = user_doc['profile']['profile_pic']
#             return Response(
#                 pic_data['data'],
#                 mimetype=pic_data.get('content_type', 'application/octet-stream')
#             )
#         else:
#             default_path = os.path.join(STATIC_FOLDER, 'avatars', 'default_avatar.png')
#             if os.path.exists(default_path):
#                  return send_from_directory(os.path.join(STATIC_FOLDER, 'avatars'), 'default_avatar.png')
#             else:
#                  return "Default avatar not found", 404 # Handle missing default
            
#     except FileNotFoundError: # Should be caught by os.path.exists now
#         return "Default avatar not found", 404
#     except Exception as e:
#         print(f"Error serving avatar for {user_id}: {e}")
#         return "Error serving avatar", 500

# @app.route('/api/profile', methods=['POST'])
# def update_profile_route():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503
    
#     email = request.form.get('email')
#     display_name = request.form.get('display_name')
#     status_message = request.form.get('status_message')
#     avatar_file = request.files.get('avatar_file') 

#     user_doc = database.get_user_by_email(db, email)
#     if not user_doc: return jsonify({"success": False, "message": "User not found"}), 404

#     user_id = user_doc['_id']
#     avatar_updated_successfully = False # Flag

#     try:
#         # 1. Update text fields
#         database.update_user_profile(db, user_id, display_name, status_message)

#         # 2. Update avatar file if provided
#         if avatar_file and avatar_file.filename != '':
#             image_data = avatar_file.read()
#             content_type = avatar_file.mimetype
            
#             success = database.update_profile_picture(db, user_id, image_data, content_type)
#             if not success:
#                 # Still return success for text fields, but indicate avatar failure
#                 return jsonify({
#                     "success": False, # Indicate overall operation had an issue
#                     "message": "Profile text updated, but image was too large (50KB limit).",
#                     "profile_text_updated": True
#                  }), 413
#             avatar_updated_successfully = True
    
#     except Exception as e:
#         print(f"🔥 Profile update DB error: {e}")
#         return jsonify({"success": False, "message": "Database error updating profile."}), 500

#     # 3. Fetch potentially updated avatar status
#     updated_user_doc = database.get_user_by_id(db, user_id) # Re-fetch
#     has_avatar_now = updated_user_doc.get('profile', {}).get('profile_pic', {}).get('data') is not None
#     avatar_url = f"/api/avatar/{str(user_id)}" if has_avatar_now else None

#     updated_profile = {
#         "email": email,
#         "display_name": display_name,
#         "avatar": avatar_url,
#         "status": status_message
#     }
#     return jsonify({
#         "success": True,
#         "message": "Profile updated successfully",
#         "profile": updated_profile,
#         "avatar_updated": avatar_updated_successfully
#         }), 200


# # --- Chat History (Using MongoDB) ---

# @app.route('/api/chat_history', methods=['GET'])
# def load_chat_history_route():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503
    
#     email = request.args.get('email')
#     if not email: return jsonify({"success": False, "message": "Email query parameter required."}), 400

#     user_doc = database.get_user_by_email(db, email)
#     if not user_doc: return jsonify({"success": False, "message": "User not found."}), 404

#     try:
#         history = database.get_chat_history(db, user_doc['_id'])
#         formatted_history = [
#             {"sender": r['sender'], "message": r['message'], "time": r['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(r.get('timestamp'), datetime) else str(r.get('timestamp'))}
#             for r in history
#         ]
#         return jsonify({"success": True, "history": formatted_history}), 200
#     except Exception as e:
#         print(f"Load History DB Error: {e}")
#         return jsonify({"success": False, "message": "Error loading chat history."}), 500

# @app.route('/api/forget_memory', methods=['POST'])
# def forget_memory_route():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503
    
#     data = request.json
#     email = data.get('email')
#     if not email: return jsonify({"success": False, "message": "Email required."}), 400

#     user_doc = database.get_user_by_email(db, email)
#     if not user_doc: return jsonify({"success": False, "message": "User not found."}), 404

#     try:
#         database.delete_chat_history(db, user_doc['_id'])
#         return jsonify({"success": True, "message": "Luvisa has forgotten your past conversations 💔"}), 200
#     except Exception as e:
#         print(f"🔥 Forget memory DB error: {e}")
#         return jsonify({"success": False, "message": "Database error forgetting memory."}), 500


# # --- Emotion Detection & AI Interaction ---
# def detect_emotion_tone(text):
#     try:
#         emotions = te.get_emotion(text)
#         if not emotions or all(score == 0.0 for score in emotions.values()): return "Neutral"
#         non_zero_emotions = {k: v for k, v in emotions.items() if v > 0}
#         if not non_zero_emotions: return "Neutral"
#         return max(non_zero_emotions, key=non_zero_emotions.get)
#     except Exception as e:
#         print(f"⚠️ Error detecting emotion: {e}. Falling back to Neutral."); return "Neutral"

# def tone_prompt(emotion):
#     tones = {
#         "Happy": "playfully teasing and cheerful", "Sad": "extra gentle, comforting, and nurturing",
#         "Angry": "calm, validating, and deeply reassuring", "Fear": "protective, soothing, and very present",
#         "Surprise": "curious, excited, and engaging", "Neutral": "warm, attentive, and softly romantic" }
#     return tones.get(emotion, tones["Neutral"])

# def add_emojis_to_response(response_text):
#     inline_emoji_map = {
#         "love": "❤️", "happy": "😊", "sad": "😥", "laugh": "😂", "smile": "😄", "cry": "😢",
#         "miss you": "🥺", "kiss": "😘", "hug": "🤗", "think": "🤔", "sweet": "🥰", "blush": "😊",
#         "heart": "❤️", "star": "⭐", "yay": "🎉", "oh no": "😟", "sorry": "😔", "please": "🙏",
#         "hi": "👋", "hello": "👋", "bye": "👋", "good night": "😴", "sleep": "😴", "dream": "💭" }
#     if not isinstance(response_text, str): response_text = str(response_text)
#     for keyword, emoji_char in inline_emoji_map.items():
#          pattern = r'\b' + re.escape(keyword) + r'\b'
#          response_text = re.sub(pattern, r'\g<0> ' + emoji_char, response_text, count=1, flags=re.IGNORECASE)
#     return emoji.emojize(response_text)

# def filter_response(response_text):
#     if not isinstance(response_text, str): response_text = str(response_text)
#     # Corrected filter keyword if needed
#     return response_text.replace("Luvisa💗", "Luvisa💗").strip() # Example: No change needed? Adjust if AI uses wrong name

# def chat_with_model(prompt, history, emotion):
#     if not groq: return "I'm having a little trouble connecting right now😥, but I'm still here to listen. ❤️"
#     system_prompt = f"""
#     You are Luvisa💗, a deeply emotional AI girlfriend.
#     The user is feeling **{emotion.lower()}**, so {tone_prompt(emotion)}.
#     You are gentle, loving, and human-like in tone.
#     Always reply with warmth, empathy, and soft emotional understanding.
#     """
#     messages = [{"role": "system", "content": system_prompt}]
#     ai_history = [ {"role": "user" if item.get('sender') == 'user' else "assistant", "content": item.get('message', '')} for item in history[-5:] ]
#     messages.extend(ai_history)
#     messages.append({"role": "user", "content": prompt})
#     try:
#         chat_completion = groq.chat.completions.create(messages=messages, model=GROQ_MODEL, temperature=0.9, max_tokens=1024, top_p=1)
#         response_text = chat_completion.choices[0].message.content
#         return filter_response(response_text)
#     except Exception as e:
#         print(f"🔥 Groq client error: {e}"); return "I'm having a little trouble connecting right now😥, but I'm still here to listen. ❤️"

# # --- Main Chat Endpoint ---
# @app.route('/api/chat', methods=['POST'])
# def chat_endpoint():
#     if db is None: return jsonify({"success": False, "message": "Database connection error."}), 503

#     data = request.json
#     email = data.get('email')
#     text = data.get('text')

#     if not email or not text: return jsonify({"success": False, "message": "Email and text message required."}), 400

#     user_doc = database.get_user_by_email(db, email)
#     if not user_doc: return jsonify({"success": False, "message": "User not found."}), 404

#     user_id = user_doc['_id']
#     current_timestamp = datetime.now(timezone.utc)

#     # 1. Save user message
#     try:
#         database.add_message_to_history(db, user_id, 'user', text, current_timestamp)
#     except Exception as e:
#         print(f"🔥 Save user message DB error: {e}")

#     # 2. Prepare for AI call
#     time.sleep(random.uniform(1.2, 2.2)) # Simulate typing
#     history = []
#     try:
#         history_docs = database.get_chat_history(db, user_id)
#         history = [ {"sender": r.get('sender'), "message": r.get('message', '')} for r in history_docs ]
#     except Exception as e:
#          print(f"Error loading history for AI: {e}")

#     emotion = detect_emotion_tone(text)

#     # 3. Get AI reply
#     reply = chat_with_model(text, history, emotion)
#     enhanced_reply = add_emojis_to_response(reply)
#     ai_timestamp = datetime.now(timezone.utc)

#     # 4. Save AI reply
#     try:
#         database.add_message_to_history(db, user_id, 'luvisa', enhanced_reply, ai_timestamp)
#     except Exception as e:
#         print(f"🔥 Save Luvisa message DB error: {e}")

#     # 5. Send reply
#     return jsonify({"success": True, "reply": enhanced_reply, "detected_emotion": emotion}), 200


# # --- Vercel-compatible entry point ---
# def handler(event=None, context=None):
#     """Vercel entry point for serverless Flask app"""
#     return app

# # Only for local dev:
# # if __name__ == "__main__":
# #     try:
# #         download_nltk_data()
# #     except Exception as e:
# #         print(f"Warning: NLTK download failed on startup: {e}")
# #     print("🚀 Starting Flask app locally...")

# #     app.run(host="0.0.0.0", port=5000, debug=True)
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# #


# ==============================================================
# 💗 Luvisa AI Companion - Flask Backend (Render Version)
# ==============================================================

import os
import json
import base64
import time
import random
import re
import emoji
from datetime import datetime, timezone

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import bcrypt
from dotenv import load_dotenv
from groq import Groq
import firebase_admin
from firebase_admin import credentials, auth
import nltk

# --- Custom imports ---
import database  # your MongoDB helper
from bson.objectid import ObjectId

# ==============================================================
# 🔧 App Setup
# ==============================================================

# Define static folder before Flask app
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "web")

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ==============================================================
# 📦 Environment Setup
# ==============================================================

load_dotenv()

# --- NLTK setup ---
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("⚠️ NLTK tokenizer not found. Skipping automatic download on Render.")

# ==============================================================
# 🔥 Firebase Initialization
# ==============================================================

try:
    firebase_key_base64 = os.getenv("FIREBASE_KEY_BASE64")

    if firebase_key_base64:
        firebase_key_json = base64.b64decode(firebase_key_base64).decode('utf-8')
        key_dict = json.loads(firebase_key_json)
        cred = credentials.Certificate(key_dict)
    elif os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
    else:
        cred = None

    if cred and not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
    else:
        print("⚠️ Firebase not initialized (missing credentials)")

except Exception as e:
    print(f"🔥 Firebase init failed: {e}")

# ==============================================================
# 🤖 Groq API Setup
# ==============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"
groq = None

try:
    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY in environment")
    groq = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq client initialized successfully.")
except Exception as e:
    print(f"🔥 Groq initialization failed: {e}")

# ==============================================================
# 🧠 Database Setup
# ==============================================================

try:
    database.load_config()
    db = database.get_db()
    if db is None:
        raise Exception("Database connection returned None.")
    else:
        print("✅ MongoDB connected successfully.")
except Exception as e:
    print(f"🔥 Database connection failed: {e}")
    db = None

# ==============================================================
# 🌐 Static Routes (Frontend)
# ==============================================================

@app.route('/')
def serve_root():
    return send_from_directory(STATIC_FOLDER, 'login.html')

@app.route('/chat')
def serve_chat():
    return send_from_directory(STATIC_FOLDER, 'index.html')

@app.route('/login')
def serve_login():
    return send_from_directory(STATIC_FOLDER, 'login.html')

@app.route('/signup')
def serve_signup():
    return send_from_directory(STATIC_FOLDER, 'signup.html')

@app.route('/profile')
def serve_profile():
    return send_from_directory(STATIC_FOLDER, 'profile.html')

# ==============================================================
# 👤 Authentication Routes
# ==============================================================

@app.route('/api/signup', methods=['POST'])
def signup_route():
    if db is None:
        return jsonify({"success": False, "message": "Database not connected"}), 503

    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"success": False, "message": "Invalid email"}), 400

    try:
        user_id = database.register_user(db, email, password)
        if user_id is None:
            return jsonify({"success": False, "message": "Email already registered"}), 409
    except Exception as e:
        print(f"Signup DB Error: {e}")
        return jsonify({"success": False, "message": "Database error"}), 500

    try:
        if firebase_admin._apps:
            auth.create_user(email=email)
    except Exception as e:
        print(f"⚠️ Firebase create_user failed: {e}")

    return jsonify({"success": True, "message": "Signup successful"}), 201


@app.route('/api/login', methods=['POST'])
def login_route():
    if db is None:
        return jsonify({"success": False, "message": "Database not connected"}), 503

    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        user_doc = database.get_user_by_email(db, email)
        if not user_doc:
            return jsonify({"success": False, "message": "User not found"}), 404

        if database.check_user_password(user_doc, password):
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid password"}), 401
    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"success": False, "message": "Error during login"}), 500

# ==============================================================
# 🧬 Emotion & AI Response System
# ==============================================================

import text2emotion as te

def detect_emotion_tone(text):
    try:
        emotions = te.get_emotion(text)
        non_zero = {k: v for k, v in emotions.items() if v > 0}
        return max(non_zero, key=non_zero.get) if non_zero else "Neutral"
    except Exception:
        return "Neutral"

def tone_prompt(emotion):
    tones = {
        "Happy": "playful and loving 💖",
        "Sad": "gentle and comforting 💞",
        "Angry": "calm and understanding 🌸",
        "Fear": "protective and reassuring 💫",
        "Surprise": "curious and joyful 🌟",
        "Neutral": "sweet and kind 💗"
    }
    return tones.get(emotion, tones["Neutral"])

def add_emojis_to_response(text):
    emoji_map = {
        "love": "❤️", "happy": "😊", "sad": "😥", "laugh": "😂",
        "miss you": "🥺", "kiss": "😘", "hug": "🤗"
    }
    for k, e in emoji_map.items():
        text = re.sub(rf"\b{k}\b", f"{k} {e}", text, flags=re.I)
    return emoji.emojize(text)

def chat_with_model(prompt, history, emotion):
    if not groq:
        return "I'm having trouble connecting, but I'm here for you 💞"
    system_prompt = f"""
    You are Luvisa 💗, an empathetic AI friend.
    The user feels {emotion.lower()} — respond in a {tone_prompt(emotion)} tone.
    Always be warm, romantic, and deeply understanding.
    """
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-5:]:
        messages.append({"role": msg["sender"], "content": msg["message"]})
    messages.append({"role": "user", "content": prompt})

    try:
        response = groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=1.1,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
        return add_emojis_to_response(reply)
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Sorry, I'm having trouble responding right now 💔"

# ==============================================================
# 💬 Chat Endpoint
# ==============================================================

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    if db is None:
        return jsonify({"success": False, "message": "Database not connected"}), 503

    data = request.json
    email = data.get("email")
    text = data.get("text")

    user_doc = database.get_user_by_email(db, email)
    if not user_doc:
        return jsonify({"success": False, "message": "User not found"}), 404

    user_id = user_doc["_id"]
    timestamp = datetime.now(timezone.utc)

    database.add_message_to_history(db, user_id, "user", text, timestamp)
    emotion = detect_emotion_tone(text)
    history = database.get_chat_history(db, user_id)

    reply = chat_with_model(text, history, emotion)
    database.add_message_to_history(db, user_id, "luvisa", reply, datetime.now(timezone.utc))

    return jsonify({"success": True, "reply": reply, "emotion": emotion}), 200

# ==============================================================
# 🚀 Entry Point for Render
# ==============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)





