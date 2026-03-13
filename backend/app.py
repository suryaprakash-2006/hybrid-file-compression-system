from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
COMPRESSED_FOLDER = "compressed"


# -----------------------------
# RLE COMPRESSION
# -----------------------------
def rle_compress(data):

    if not data:
        return ""

    result = ""
    count = 1

    for i in range(1, len(data)):

        if data[i] == data[i-1]:
            count += 1
        else:
            result += str(count) + data[i-1]
            count = 1

    result += str(count) + data[-1]

    return result


# -----------------------------
# RLE DECOMPRESSION
# -----------------------------
def rle_decompress(data):

    result = ""
    count = ""

    for ch in data:

        if ch.isdigit():
            count += ch
        else:
            result += ch * int(count)
            count = ""

    return result


# -----------------------------
# INTEGRITY VERIFICATION
# -----------------------------
def verify(original, decompressed):

    with open(original, "rb") as f1:
        d1 = f1.read()

    with open(decompressed, "rb") as f2:
        d2 = f2.read()

    return d1 == d2


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# COMPRESS
# -----------------------------
@app.route("/compress", methods=["POST"])
def compress():

    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, "r") as f:
        data = f.read()

    compressed_data = rle_compress(data)

    output_file = file.filename + ".hfc"
    output_path = os.path.join(COMPRESSED_FOLDER, output_file)

    with open(output_path, "w") as f:
        f.write(compressed_data)

    original_size = os.path.getsize(filepath)
    compressed_size = os.path.getsize(output_path)

    ratio = ((original_size - compressed_size) / original_size) * 100

    print("Compression complete")
    print("Original Size:", original_size)
    print("Compressed Size:", compressed_size)

    return send_file(output_path, as_attachment=True)


# -----------------------------
# DECOMPRESS
# -----------------------------
@app.route("/decompress", methods=["POST"])
def decompress():

    file = request.files["file"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, "r") as f:
        data = f.read()

    decompressed_data = rle_decompress(data)

    output_path = os.path.join(COMPRESSED_FOLDER, "decompressed.txt")

    with open(output_path, "w") as f:
        f.write(decompressed_data)

    print("Decompression complete")

    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)