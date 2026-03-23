from flask import Flask, render_template, request, send_file
from pathlib import Path
from uuid import uuid4
import hashlib
import os
import shutil
import subprocess
import tempfile

from werkzeug.utils import secure_filename

app = Flask(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT_DIR / "uploads"
COMPRESSED_DIR = ROOT_DIR / "compressed"
ENGINE_DIR = ROOT_DIR / "engine"

ASM_COMPRESS_COM = ENGINE_DIR / "compression.com"
ASM_DECOMPRESS_COM = ENGINE_DIR / "decompression.com"

for directory in (UPLOAD_DIR, COMPRESSED_DIR):
    directory.mkdir(parents=True, exist_ok=True)


# -----------------------------
# RLE COMPRESSION
# -----------------------------
def rle_compress(data):

    if not data:
        return ""

    result = []
    count = 1

    for i in range(1, len(data)):

        if data[i] == data[i - 1]:
            count += 1
        else:
            result.append(str(count))
            result.append(data[i - 1])
            count = 1

    result.append(str(count))
    result.append(data[-1])

    return "".join(result)


# -----------------------------
# RLE DECOMPRESSION
# -----------------------------
def rle_decompress(data):

    result = []
    count = ""

    for ch in data:

        if ch.isdigit():
            count += ch
        else:
            if not count:
                raise ValueError("Invalid RLE stream: missing count before symbol")
            result.append(ch * int(count))
            count = ""

    if count:
        raise ValueError("Invalid RLE stream: trailing count without symbol")

    return "".join(result)


# -----------------------------
# INTEGRITY VERIFICATION
# -----------------------------
def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        while True:
            chunk = file_handle.read(8192)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify(original: Path, decompressed: Path) -> bool:
    return file_sha256(original) == file_sha256(decompressed)


def save_upload(file_storage) -> tuple[Path, str]:
    safe_name = secure_filename(file_storage.filename or "")
    if not safe_name:
        raise ValueError("No file selected")

    stored_name = f"{uuid4().hex}_{safe_name}"
    saved_path = UPLOAD_DIR / stored_name
    file_storage.save(saved_path)
    return saved_path, safe_name


def choose_engine(preferred_engine: str, original_name: str) -> str:
    if preferred_engine in {"python", "8086"}:
        return preferred_engine

    suffix = Path(original_name).suffix.lower()
    if suffix == ".txt":
        return "8086"
    return "python"


def resolve_dosbox_path() -> str | None:
    env_path = os.environ.get("DOSBOX_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path

    for candidate in ("dosbox", "dosbox-x"):
        found = shutil.which(candidate)
        if found:
            return found

    common_paths = [
        Path(r"C:\Program Files (x86)\DOSBox-0.74-3\DOSBox.exe"),
        Path(r"C:\Program Files\DOSBox-0.74-3\DOSBox.exe"),
        Path(r"C:\Program Files (x86)\DOSBox-0.74\DOSBox.exe"),
        Path(r"C:\Program Files\DOSBox-0.74\DOSBox.exe"),
        Path(r"C:\Program Files\DOSBox-X\dosbox-x.exe"),
        Path(r"C:\Program Files (x86)\DOSBox-X\dosbox-x.exe"),
    ]
    for candidate_path in common_paths:
        if candidate_path.exists():
            return str(candidate_path)

    return None


def run_asm_program(program_path: Path, input_path: Path, output_name: str, output_path: Path) -> None:
    if not program_path.exists():
        raise FileNotFoundError(f"Missing 8086 program: {program_path}")

    dosbox_path = resolve_dosbox_path()
    if dosbox_path is None:
        raise RuntimeError("DOSBox runtime not found")

    with tempfile.TemporaryDirectory(prefix="hfc_asm_") as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_input = temp_dir_path / "input.txt"
        temp_program = temp_dir_path / "RUNNER.COM"
        temp_output = temp_dir_path / output_name

        shutil.copy2(input_path, temp_input)
        shutil.copy2(program_path, temp_program)

        command = [
            dosbox_path,
            "-noconsole",
            "-noautoexec",
            "-c",
            f"mount c \"{temp_dir}\"",
            "-c",
            "c:",
            "-c",
            "RUNNER",
            "-c",
            "exit",
        ]

        subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=25,
            check=True,
        )

        if not temp_output.exists():
            raise RuntimeError(f"8086 engine did not create {output_name}")

        shutil.copy2(temp_output, output_path)


def compress_with_python(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as file_handle:
        data = file_handle.read()

    compressed_data = rle_compress(data)

    with output_path.open("w", encoding="utf-8") as file_handle:
        file_handle.write(compressed_data)


def decompress_with_python(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as file_handle:
        data = file_handle.read()

    decompressed_data = rle_decompress(data)

    with output_path.open("w", encoding="utf-8") as file_handle:
        file_handle.write(decompressed_data)


def compress_file(input_path: Path, original_name: str, preferred_engine: str) -> tuple[Path, str, str]:
    engine = choose_engine(preferred_engine, original_name)
    output_name = f"{original_name}.hfc"
    output_path = COMPRESSED_DIR / f"{uuid4().hex}_{output_name}"
    fallback_reason = ""

    if engine == "8086":
        try:
            run_asm_program(ASM_COMPRESS_COM, input_path, "output.hfc", output_path)
            return output_path, output_name, "8086"
        except (FileNotFoundError, RuntimeError, subprocess.SubprocessError) as error:
            fallback_reason = str(error)

    compress_with_python(input_path, output_path)
    engine_used = "python-fallback" if engine == "8086" else "python"
    if fallback_reason:
        engine_used = f"{engine_used}:{fallback_reason}"
    return output_path, output_name, engine_used


def decompress_file(input_path: Path, original_name: str, preferred_engine: str) -> tuple[Path, str, str]:
    engine = choose_engine(preferred_engine, original_name)
    base_name = Path(original_name).stem
    output_name = f"{base_name}.decompressed.txt"
    output_path = COMPRESSED_DIR / f"{uuid4().hex}_{output_name}"
    fallback_reason = ""

    if engine == "8086":
        try:
            run_asm_program(ASM_DECOMPRESS_COM, input_path, "output.txt", output_path)
            return output_path, output_name, "8086"
        except (FileNotFoundError, RuntimeError, subprocess.SubprocessError) as error:
            fallback_reason = str(error)

    decompress_with_python(input_path, output_path)
    engine_used = "python-fallback" if engine == "8086" else "python"
    if fallback_reason:
        engine_used = f"{engine_used}:{fallback_reason}"
    return output_path, output_name, engine_used


def build_download_response(output_path: Path, output_name: str, engine_used: str):
    response = send_file(output_path, as_attachment=True, download_name=output_name)
    response.headers["X-Engine-Used"] = engine_used
    return response


@app.route("/engine-status")
def engine_status():
    return {
        "compression_program": ASM_COMPRESS_COM.exists(),
        "decompression_program": ASM_DECOMPRESS_COM.exists(),
        "dosbox_available": resolve_dosbox_path() is not None,
    }


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
    uploaded_file = request.files.get("file")
    preferred_engine = request.form.get("engine", "auto").lower()

    if uploaded_file is None:
        return "No file selected", 400

    try:
        input_path, original_name = save_upload(uploaded_file)
        output_path, output_name, engine_used = compress_file(input_path, original_name, preferred_engine)
    except ValueError as error:
        return str(error), 400
    except UnicodeDecodeError:
        return "Selected engine requires a text file", 400
    except Exception as error:
        return f"Compression failed: {error}", 500

    return build_download_response(output_path, output_name, engine_used)


# -----------------------------
# DECOMPRESS
# -----------------------------
@app.route("/decompress", methods=["POST"])
def decompress():
    uploaded_file = request.files.get("file")
    preferred_engine = request.form.get("engine", "auto").lower()

    if uploaded_file is None:
        return "No file selected", 400

    try:
        input_path, original_name = save_upload(uploaded_file)
        output_path, output_name, engine_used = decompress_file(input_path, original_name, preferred_engine)
    except ValueError as error:
        return str(error), 400
    except UnicodeDecodeError:
        return "Selected engine requires a text file", 400
    except Exception as error:
        return f"Decompression failed: {error}", 500

    return build_download_response(output_path, output_name, engine_used)


@app.route("/verify", methods=["POST"])
def verify_files():
    original_file = request.files.get("original")
    decompressed_file = request.files.get("decompressed")

    if original_file is None or decompressed_file is None:
        return "Both original and decompressed files are required", 400

    try:
        original_path, _ = save_upload(original_file)
        decompressed_path, _ = save_upload(decompressed_file)
    except ValueError as error:
        return str(error), 400

    return {
        "match": verify(original_path, decompressed_path),
        "original_sha256": file_sha256(original_path),
        "decompressed_sha256": file_sha256(decompressed_path),
    }


if __name__ == "__main__":
    app.run(debug=True)