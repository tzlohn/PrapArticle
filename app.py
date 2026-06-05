from flask import Flask, render_template, request, jsonify
#from openai import OpenAI
import os,re

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json()
    text = data.get("text", "")

    # Build a regex that matches a preposition optionally followed by an article.
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

    new_text = pattern.sub(repl, text)

    # Debug: log received text to server console and include it in response
    print("[generate] received text:", repr(text))

    response = {
        "text": new_text,
        "answers": answers,
        "received_text": text
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