from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import json
import requests
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5vl:3b"


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    if "photo" not in request.files:
        return "Please select a photo.", 400

    photo = request.files["photo"]

    if not photo.filename or not allowed_file(photo.filename):
        return "Please upload a JPG, PNG or WEBP image.", 400

    filename = str(uuid.uuid4()) + "_" + secure_filename(photo.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    photo.save(filepath)

    style = request.form.get("style", "natural")
    image_path = "/" + filepath.replace("\\", "/")

    try:
        import base64

        with open(filepath, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        prompt = f"""
        Analyse the actual image carefully.
        Write in this style: {style}.

        Return valid JSON only with these keys:
        caption: a suitable social media caption
        hashtags: 5 to 10 relevant hashtags
        description: a factual description of the visible image
        mood: the likely mood of the image
        song: a suitable music genre or song suggestion

        Do not invent objects or activities that are not visible.
        If uncertain, be cautious.
        """

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "images": [image_data],
                "stream": False,
                "format": "json"
            },
            timeout=180
        )
        response.raise_for_status()

        ai_text = response.json()["response"]
        result = json.loads(ai_text)
        result["image"] = image_path

    except requests.exceptions.ConnectionError:
        result = {
            "error": "AI is not connected. Start Ollama on your laptop and try again."
        }
    except requests.exceptions.Timeout:
        result = {
            "error": "AI took too long to respond. Please try again."
        }
    except (requests.RequestException, ValueError, KeyError):
        result = {
            "error": "Could not analyse this photo. Check your AI model and try again."
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
