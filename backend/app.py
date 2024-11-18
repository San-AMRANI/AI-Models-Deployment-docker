from flask import Flask, request, render_template_string
from openai import OpenAI

app = Flask(__name__)

# Initialize the NVIDIA OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# HTML template
template = """
<html>
  <body>
    <h1>Interact with LLaMA Model</h1>
    <form action="/" method="post">
      <textarea name="user_input" placeholder="Type your question or topic here..."></textarea>
      <input type="submit" value="Ask">
    </form>
    <div>
      {% if response %}
        <h2>Model's Response:</h2>
        <pre>{{ response }}</pre>
      {% endif %}
    </div>
  </body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        try:
            # Get streaming completion response
            completion = client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "user", "content": user_input}],
                temperature=0.5,
                top_p=1,
                max_tokens=1024,
                stream=True  # Enable streaming
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
    return render_template_string(template, response=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
