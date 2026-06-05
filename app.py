from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

PROMPT = """
You are a German language teacher.

Task:
1. Find every German preposition.
2. Remove the preposition.
3. Remove the article immediately following it if present.
4. Replace each removed word with an underline.

Examples:

Ich gehe in die Schule.
→ Ich gehe ____ ____ Schule.

Das Buch liegt auf dem Tisch.
→ Das Buch liegt ____ ____ Tisch.

Return ONLY the modified text.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json()
    text = data.get("text", "")

    response = client.responses.create(
        model="gpt-5.4-nano",
        input=[
            {
                "role": "system",
                "content": """
Return ONLY valid JSON in this format:

{
  "text": "sentence with [1] [2] blanks",
  "answers": {
    "1": "in",
    "2": "die"
  }
}
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    # 🔥 IMPORTANT FIX: parse JSON string into Python dict
    import json
    result = json.loads(response.output_text)

    return jsonify(result)


if __name__ == "__main__":
    app.run()