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

    text = request.json["text"]

    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return jsonify({
        "result": response.output_text
    })


if __name__ == "__main__":
    app.run(debug=True)