from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from openai import OpenAI

# Configuration
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
API_TOKEN = "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"  # Your provided token
headers = {"Authorization": f"Bearer {API_TOKEN}"}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

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


# Route for handling audio uploads
@app.route("/model1", methods=["POST"])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the file
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)

    # Query the Whisper model
    result = query_audio(file_path)

    # Remove the file after processing
    os.remove(file_path)

    # Handle response
    if "error" in result:
        return jsonify({"error": result.get("message", "Unknown error")}), 500

    transcription = result.get("text", "No transcription available")
    return jsonify({"text": transcription}), 200


@app.route("/chat", methods=["POST"])
def query_text():
    response = None
    if request.method == 'POST':
        user_input = request.json.get('chatInput')  # Expecting JSON data from frontend
        try:
            # Get streaming completion response from the model
            completion = client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "user", "content": user_input}],
                temperature=0.7,
                top_p=1,
                max_tokens=150,
                stream=True  # Streaming responses
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

    # Return the response as JSON
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
