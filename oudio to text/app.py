import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Replace with your actual token
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
API_TOKEN = "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"  # Your provided token
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Function to query the Whisper model
def query_audio(filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()  # Whisper model typically returns a JSON with transcriptions
        else:
            return {"error": response.status_code, "message": response.text}
    except Exception as e:
        return {"error": "Request failed", "message": str(e)}

# Route for home page with audio upload
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Check if a file is uploaded
        if 'audio' not in request.files:
            return render_template("index.html", error="No file uploaded")

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return render_template("index.html", error="No file selected")

        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
        audio_file.save(file_path)

        # Query the Whisper model
        result = query_audio(file_path)

        # Remove the file after processing
        os.remove(file_path)

        # Handle response
        if "error" in result:
            return render_template("index.html", error=result.get("message", "Unknown error"))

        transcription = result.get("text", "No transcription available")
        return render_template("index.html", transcription=transcription)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
