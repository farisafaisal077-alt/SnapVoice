from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

    if photo.filename == "":
        return "Please select a photo.", 400

    if not allowed_file(photo.filename):
        return "Upload a JPG, PNG, or WEBP image.", 400

    filename = secure_filename(photo.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    photo.save(filepath)

    # Temporary demo results.
    # We will connect real AI image analysis next.
    result = {
        "caption": "Little moments, beautiful memories ✨",
        "hashtags": "#SnapVoice #PhotoOfTheDay #Memories",
        "description": "Your photo is ready for its story.",
        "song": "Suggested mood: chill and feel-good",
        "image": "/" + filepath.replace("\\", "/"),
    }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
