from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Compression route
@app.route("/compress", methods=["POST"])
def compress():

    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Detect file type
    ext = file.filename.split(".")[-1]

    if ext == "txt":
        print("Text file detected → using 8086 compression engine")
    else:
        print("Other file type → using Python compression module")

    return f"{file.filename} uploaded successfully. Compression will run here."


if __name__ == "__main__":
    app.run(debug=True)