from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_URL = "http://localhost:5000/upload"  # Измени на внешний адрес, если нужно

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    file = request.files.get("file")
    if not file:
        return "Файл не выбран", 400

    response = requests.post(API_URL, files={"file": file})
    return f"Ответ от сервера: {response.text}"

if __name__ == "__main__":
    app.run(debug=True, port=5050)
