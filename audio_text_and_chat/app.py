import os
import requests
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Environment variable for the API token
API_TOKEN = os.getenv("API_TOKEN", "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")
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

@app.route("/")
def index():
    # Render the HTML page
    return render_template("index.html")


@app.route("/chat", methods=["GET", "POST"])
def query_text():
    response = None
    if request.method == 'POST':
        user_input = request.form['chatInput']
        try:
            # Get streaming completion response
            completion = client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role":"user","content":user_input}],
                temperature=0.5,
                top_p=1,
                max_tokens=1024,
                stream=True
            )

            # Process chunks and concatenate the content
            response_chunks = []
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_chunks.append(chunk.choices[0].delta.content)

            # Join all chunks into a single string
            response = ''.join(response_chunks)

        except Exception as e:
            response = f"An error occurred: {str(e)}"
    return jsonify({
        "response": response
    })


# Route for home page with audio upload
@app.route("/audio-to-text", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Check if a file is uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Validate file type
        if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a')):
            return jsonify({'error': 'Invalid file type. Please upload an audio file.'}), 400

        # Save the file securely
        file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
        audio_file.save(file_path)

        # Query the Whisper model
        result = query_audio(file_path)

        # Remove the file after processing
        os.remove(file_path)

        # Handle response
        if "error" in result:
            return jsonify({'error': result.get("message", "Unknown error")}), 500

        transcription = result.get("text", "No transcription available")
        return jsonify({'transcription': transcription})

    return jsonify({"message": "Upload an audio file to transcribe."})


# Function to query the Whisper model
def query_audio(filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": response.status_code,
                "message": response.json().get("error", response.text)
            }
    except Exception as e:
        return {"error": "Request failed", "message": str(e)}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
