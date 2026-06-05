from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

PROMPT = """
You are a precise German grammar transformation engine.

Your task is to convert German sentences into fill-in-the-blank exercises.

RULES (must follow strictly):
1. Scan the entire input text and find EVERY occurrence of a German preposition.
2. If a preposition is directly followed by an article (der, die, das, den, dem, des, ein, eine, einen, einem, einer), remove BOTH words.
3. EACH removed word (preposition and article) must be replaced with its own blank in the form [n], where n is a running number starting from 1.
4. Do NOT skip any occurrence.
5. Do NOT stop after the first or second match.
6. Continue until the entire text is processed.
7. Keep all other words unchanged.
8. Maintain original sentence structure.

OUTPUT FORMAT (strict):
Return ONLY valid JSON in this exact structure:

{
  "text": "sentence with [1] [2] ... blanks",
  "answers": {
    "1": "removed word 1",
    "2": "removed word 2"
  }
}

EXAMPLES:

Input:
Ich gehe in die Schule.

Output:
{
  "text": "Ich gehe [1] [2] Schule.",
  "answers": {
    "1": "in",
    "2": "die"
  }
}

Input:
Das Buch liegt auf dem Tisch.

Output:
{
  "text": "Das Buch liegt [1] [2] Tisch.",
  "answers": {
    "1": "auf",
    "2": "dem"
  }
}

IMPORTANT:
- Every valid occurrence MUST be converted.
- Each removed word must get its own blank.
- Never return partial transformations.
- Never return explanations or extra text.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json()
    text = data.get("text", "")

    response = client.responses.create(
        model="gpt-5.4",
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

    # 🔥 IMPORTANT FIX: parse JSON string into Python dict
    import json
    result = json.loads(response.output_text)

    return jsonify(result)


if __name__ == "__main__":
    app.run()