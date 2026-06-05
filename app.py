from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os,re

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["GET"])
def generate():
    # Check if API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEY environment variable is not set"}), 500
    
    # Generate German text using OpenAI GPT API
    prompt = "Please help me to generate a 100-word german text in A2 level"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] OpenAI API error: {str(e)}")
        return jsonify({"error": f"Failed to generate text: {str(e)}"}), 500

    # Process the generated text: remove prepositions and articles
    ARTICLES = {"der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem", "einer"}

    preps_alternation = r"|".join(re.escape(p) for p in sorted(GERMAN_PREPOSITIONS, key=len, reverse=True))
    arts_alternation = r"|".join(re.escape(a) for a in sorted(ARTICLES, key=len, reverse=True))

    pattern = re.compile(r"\b(" + preps_alternation + r")\b(?:\s+(" + arts_alternation + r"))?", flags=re.IGNORECASE)

    answers = {}
    counter = {"n": 0}

    def repl(m):
        # m.group(1) == preposition, m.group(2) == optional article
        parts = []
        counter["n"] += 1
        answers[str(counter["n"])] = m.group(1)
        parts.append(f"[{counter['n']}]")

        if m.group(2):
            counter["n"] += 1
            answers[str(counter["n"])] = m.group(2)
            parts.append(f"[{counter['n']}]")

        return " ".join(parts)

    new_text = pattern.sub(repl, generated_text)

    response = {
        "text": new_text,
        "answers": answers
    }

    return jsonify(response)

GERMAN_PREPOSITIONS = {
    "an","am","auf","hinter","in","im","ins","neben","über","unter","vor","zwischen",
    "aus","außer","bei","mit","nach","seit","von","vom","zu","zum","zur","durch","für",
    "gegen","ohne","um"}

word_re = re.compile(r"\b\w+\b", flags=re.UNICODE)
prep_pattern = re.compile(
    r"\b(" + r"|".join(re.escape(p) for p in sorted(GERMAN_PREPOSITIONS, key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE
)

def identify_prepositions(text):
    """
    Return a list of (word, is_preposition) in the order they appear.
    Words include alphabetic tokens; punctuation is ignored.
    """
    words = word_re.findall(text)
    return [(w, w.lower() in GERMAN_PREPOSITIONS) for w in words]

def mark_prepositions(text, marker_start="<mark>", marker_end="</mark>"):
    """
    Return the text with prepositions wrapped by marker_start/marker_end.
    Preserves original case and punctuation.
    """
    def repl(m):
        return f"{marker_start}{m.group(0)}{marker_end}"
    return prep_pattern.sub(repl, text)
if __name__ == "__main__":
    app.run()