import os
import json
import uuid
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from google import genai
from google.genai import types

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_FOLDER = Path("static") / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

client = None


def get_gemini_client():
    global client

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Gemini API key not found. Set GEMINI_API_KEY in Windows."
        )

    if client is None:
        client = genai.Client(api_key=api_key)

    return client


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html", result=None, error=None)


@app.route("/generate", methods=["POST"])
def generate():
    result = None
    error = None
    saved_path = None

    try:
        if "photo" not in request.files:
            raise ValueError("Please choose a photo first.")

        photo = request.files["photo"]
        style = request.form.get("style", "aesthetic")

        if not photo or photo.filename == "":
            raise ValueError("Please choose a photo first.")

        if not allowed_file(photo.filename):
            raise ValueError(
                "Please upload a PNG, JPG, JPEG, or WEBP image."
            )

        image_bytes = photo.read()

        if not image_bytes:
            raise ValueError("The selected image is empty.")

        if len(image_bytes) > 10 * 1024 * 1024:
            raise ValueError("Please upload an image smaller than 10 MB.")

        extension = secure_filename(photo.filename).rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{extension}"
        saved_path = UPLOAD_FOLDER / filename
        saved_path.write_bytes(image_bytes)

        mime_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }

        prompt = f"""
You are SnapVoice, an Instagram caption assistant.

Look carefully at the uploaded photo. Generate content based on
what is actually visible. Do not invent names, places, or events.

Preferred caption style: {style}

Return ONLY valid JSON with these exact keys:
{{
  "caption": "One engaging Instagram caption",
  "hashtags": "#RelevantTag #AnotherTag #SnapVoice",
  "description": "A short description of the photo",
  "song": "One suitable song suggestion and artist if known",
  "mood": "A short mood label"
}}

Keep the caption natural and ready to edit before posting.
Suggest a song that matches the photo's mood. Do not claim
the song is currently trending unless you can verify it.
Do not include Markdown fences around the JSON.
"""

        ai = get_gemini_client()

        response = ai.models.generate_content(
            model="gemini-flash-latest",
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_types[extension],
                ),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        result = json.loads(response.text)

        required_keys = [
            "caption",
            "hashtags",
            "description",
            "song",
            "mood",
        ]

        for key in required_keys:
            if not isinstance(result.get(key), str):
                raise RuntimeError("Gemini returned an unexpected response.")

        result["image"] = "/" + saved_path.as_posix()

    except ValueError as exc:
        error = str(exc)

    except Exception as exc:
        print("SnapVoice error:", repr(exc))
        error = (
            "Sorry, caption generation failed. Check your internet, "
            "Gemini API key, and API access, then try again."
        )

    return render_template(
        "index.html",
        result=result,
        error=error,
        **(result or {}),
    )


@app.errorhandler(413)
def file_too_large(exc):
    return render_template(
        "index.html",
        result=None,
        error="That file is too large. Please choose an image under 10 MB.",
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
