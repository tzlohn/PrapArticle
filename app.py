from flask import Flask, render_template, request, jsonify
#from openai import OpenAI
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json()
    text = data.get("text", "")

    response = {'A': 'B'}

    return jsonify(response)


if __name__ == "__main__":
    app.run()