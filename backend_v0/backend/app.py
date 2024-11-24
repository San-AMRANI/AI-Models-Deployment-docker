import os
import requests
from flask import Flask, request, jsonify, render_template

# for chat with OpenAI
from openai import OpenAI

# for image generator
import base64
from io import BytesIO
from PIL import Image


app = Flask(__name__)

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
IMAGE_FOLDER = 'static/images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Environment variable for the API token
API_TOKEN = os.getenv("API_TOKEN", "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")
API_URL_AUD = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
API_URL_IMG = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
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
        response = requests.post(API_URL_AUD, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": response.status_code,
                "message": response.json().get("error", response.text)
            }
    except Exception as e:
        return {"error": "Request failed", "message": str(e)}



# Function to query the FLUX model for image generation
def query_model(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        }
    }

    try:
        response = requests.post(API_URL_IMG, headers=headers, json=payload)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")

        if response.status_code == 200:
            # Check if response is binary image data
            if "image" in response.headers.get("Content-Type", ""):
                return {"binary_image": response.content}
            
            # Try parsing as JSON if not binary
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
            image_path = os.path.join(IMAGE_FOLDER, image_name)
            with open(image_path, 'wb') as f:
                f.write(image_data)
            return image_path
        elif image_data.startswith('data:image'):  # Base64
            img_data = base64.b64decode(image_data.split(",")[1])
            image = Image.open(BytesIO(img_data))
            image_path = os.path.join(IMAGE_FOLDER, image_name)
            image.save(image_path)
            return image_path
        else:  # URL
            img_data = requests.get(image_data).content
            image_path = os.path.join(IMAGE_FOLDER, image_name)
            with open(image_path, 'wb') as f:
                f.write(img_data)
            return image_path
    except Exception as e:
        print(f"Failed to save image: {e}")
        return None

@app.route("/image", methods=["POST"])
def generate_image():
    # Get prompt from JSON request
    data = request.get_json()
    prompt = data.get('prompt', '')
    

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400

    result = query_model(prompt)

    if "error" in result:
        return jsonify({"error": result.get("message", "Unknown error")}), 400

    # Handle different response types
    if "binary_image" in result:
        # Save binary image
        image_name = "generated_image.png"
        image_path = save_image(result["binary_image"], image_name)
    elif "image" in result:
        # Save base64 image
        image_name = "generated_image_base64.png"
        image_path = save_image(result["image"], image_name)
    elif "image_url" in result:
        # Save image from URL
        image_name = "generated_image_from_url.png"
        image_path = save_image(result["image_url"], image_name)
    else:
        # If no image data or URL
        return jsonify({"error": "No image data received"}), 400

    return jsonify({"image_path": image_path})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
