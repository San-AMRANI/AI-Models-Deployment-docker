import requests

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
API_TOKEN = "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"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Function to query the model
def query_model(prompt, max_length=100):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "temperature": 0.7,  # Adjust creativity
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Example usage
if __name__ == "__main__":
    prompt = "Explain the concept of Python decorators."
    result = query_model(prompt)
    print("Generated Response:")
    print(result)
