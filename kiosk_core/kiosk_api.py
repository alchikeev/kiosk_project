# kiosk_core/kiosk_api.py
from flask import Flask, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = "data/remote_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return {"error": "No file provided"}, 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    # 🔔 Запоминаем имя файла (или сигнализируем GUI через файл, сокет, флаг)
    with open("data/remote_files/last_file.txt", "w") as f:
        f.write(path)

    return {"status": "saved", "filename": file.filename}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
