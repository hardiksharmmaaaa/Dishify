# here we will get to the backend code and the flask code for the execution of the app

from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from PIL import Image

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

def get_gemini_response(prompt, image_data=None):
    model = genai.GenerativeModel("gemini-1.5-pro")
    if image_data:
        response = model.generate_content([prompt, image_data[0]], stream=True)
    else:
        response = model.generate_content([prompt], stream=True)

    result = ""
    for chunk in response:
        result += chunk.text
    return result

def image_setup(file):
    if file:
        bytes_data = file.read()
        return [{"mime_type": file.mimetype, "data": bytes_data}]
    return None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.form.get("prompt")
    image_file = request.files.get("image")

    if not prompt and not image_file:
        return jsonify({"error": "Please provide input"}), 400

    image_data = image_setup(image_file) if image_file else None
    try:
        response_text = get_gemini_response(prompt, image_data)
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tts", methods=["POST"])
def tts():
    text = request.form.get("text")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    tts = gTTS(text)
    audio_io = BytesIO()
    tts.write_to_fp(audio_io)
    audio_io.seek(0)
    return send_file(audio_io, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True)
