import os
import base64
import requests
from flask import Flask, request, jsonify, render_template
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Folder to save images locally
UPLOAD_FOLDER = 'static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hugging Face API details for image generation
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
API_TOKEN = "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"  # Replace with your actual token

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

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
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")

        # Save raw content to a file for debugging
        with open('debug_response_content', 'wb') as f:
            f.write(response.content)

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

# Web page to input prompt and display the generated image
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if not prompt:
            return render_template("index.html", error="Prompt cannot be empty")

        result = query_model(prompt)

        if "error" in result:
            return render_template("index.html", prompt=prompt, error=result.get("message", "Unknown error"))

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
            return render_template("index.html", prompt=prompt, error="No image data received")

        return render_template("index.html", prompt=prompt, image_path=image_path)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
