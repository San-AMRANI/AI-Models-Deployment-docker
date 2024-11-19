from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests
from openai import OpenAI
from io import BytesIO
from PIL import Image
import base64
from datetime import datetime
import uuid  # Optional: For generating unique IDs


# Configuration for image upload and generation
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hugging Face API details for image generation
IMAGE_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
IMAGE_API_TOKEN = "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"  # Replace with your actual token
headers = {"Authorization": f"Bearer {IMAGE_API_TOKEN}"}

# Configuration for audio processing (Whisper model)
AUDIO_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to query the FLUX model for image generation
def query_image_model(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        }
    }

    try:
        response = requests.post(IMAGE_API_URL, headers=headers, json=payload)
        print(f"Response Status Code: {response.status_code}")
        if response.status_code == 200:
            if "image" in response.headers.get("Content-Type", ""):
                return {"binary_image": response.content}
            try:
                result = response.json()
                return result
            except ValueError:
                return {"error": "Invalid JSON in response"}
        else:
            return {"error": response.status_code, "message": response.text}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": "Request failed", "message": str(e)}

# Function to save the image from binary, base64, or URL
def save_image(image_data, image_name):
    try:
        if isinstance(image_data, bytes):  # If binary data
            image_path = os.path.join(UPLOAD_FOLDER, image_name)
            with open(image_path, 'wb') as f:
                f.write(image_data)
            return image_path
        elif image_data.startswith('data:image'):  # Base64
            img_data = base64.b64decode(image_data.split(",")[1])
            image = Image.open(BytesIO(img_data))
            image_path = os.path.join(UPLOAD_FOLDER, image_name)
            image.save(image_path)
            return image_path
        else:  # URL
            img_data = requests.get(image_data).content
            image_path = os.path.join(UPLOAD_FOLDER, image_name)
            with open(image_path, 'wb') as f:
                f.write(img_data)
            return image_path
    except Exception as e:
        print(f"Failed to save image: {e}")
        return None

@app.route("/image", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400

    result = query_image_model(prompt)

    if "error" in result:
        return jsonify({"error": result.get("message", "Unknown error")}), 400

    # Generate a dynamic name for the image
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Format: YYYYMMDDHHMMSS
    unique_id = uuid.uuid4().hex[:8]  # Optional: Short unique ID (first 8 characters)
    base_name = "generated_image"

    if "binary_image" in result:
        image_name = f"{base_name}_{timestamp}_{unique_id}.png"
        image_path = save_image(result["binary_image"], image_name)
    elif "image" in result:
        image_name = f"{base_name}_{timestamp}_{unique_id}_base64.png"
        image_path = save_image(result["image"], image_name)
    elif "image_url" in result:
        image_name = f"{base_name}_{timestamp}_{unique_id}_from_url.png"
        image_path = save_image(result["image_url"], image_name)
    else:
        return jsonify({"error": "No image data received"}), 400

    return jsonify({"image_path": image_path})

# Function to query the Whisper model for audio transcription
def query_audio(filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(AUDIO_API_URL, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
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

    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)

    result = query_audio(file_path)

    os.remove(file_path)

    if "error" in result:
        return jsonify({"error": result.get("message", "Unknown error")}), 500

    transcription = result.get("text", "No transcription available")
    return jsonify({"text": transcription}), 200

# Route for handling text-based chat queries
@app.route("/chat", methods=["POST"])
def query_text():
    response = None
    if request.method == 'POST':
        user_input = request.json.get('chatInput')
        try:
            completion = client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "user", "content": user_input}],
                temperature=0.7,
                top_p=1,
                max_tokens=150,
                stream=True
            )

            response_chunks = []
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_chunks.append(chunk.choices[0].delta.content)

            response = ''.join(response_chunks)

        except Exception as e:
            response = f"An error occurred: {str(e)}"

    return jsonify({"response": response})

# Route to render the main page (optional)
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
