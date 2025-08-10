from flask import Flask, request, render_template, redirect, send_from_directory
import requests
import os
from datetime import datetime

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = "00KCkQLhlaDFzo5+UTu+/C4A49iLmHu7bbpsfW8iamonjEJ1s88/wdm7Yrou+FazbxY7719UNGh96EUMa8QbsG Bf9K5rDWhJpq8XTxakXRuTM6HiJDSmERbIWfyfRMfscXJPcRyTL6YyGNZxqkYSAQdB04t89/1O/w1cDnyilFU="
IMAGE_URL = "https://drive.google.com/uc?export=view&id=1GhjyvsaWP23x_wdz7n-nSqq5cziFcf1U"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

pending_answers = {}

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()

    for event in body["events"]:
        user_id = event["source"]["userId"]

        if event["type"] == "follow":
            push_image(user_id, IMAGE_URL)
            push_text(user_id, "この画像を見て答えとなる写真を送ってください！")

        elif event["type"] == "message" and event["message"]["type"] == "image":
            message_id = event["message"]["id"]
            filename = save_image_from_line(message_id)
            pending_answers[user_id] = filename
            push_text(user_id, "写真を受け取りました。判定結果をお待ちください。")

    return "OK"

@app.route("/admin")
def admin_panel():
    return render_template("judge.html", answers=pending_answers)

@app.route("/judge")
def judge():
    user_id = request.args.get("user_id")
    result = request.args.get("result")

    if result == "correct":
        push_text(user_id, "正解！")
    else:
        push_text(user_id, "不正解。もう一度考えてみよう！")

    pending_answers.pop(user_id, None)
    return redirect("/admin")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def push_text(user_id, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {"to": user_id, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=data)

def push_image(user_id, image_url):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [{
            "type": "image",
            "originalContentUrl": image_url,
            "previewImageUrl": image_url
        }]
    }
    requests.post(url, headers=headers, json=data)

def save_image_from_line(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    r = requests.get(url, headers=headers, stream=True)
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    return filename

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
from flask import Flask, request, render_template, redirect, send_from_directory
import requests
import os
from datetime import datetime

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = "00KCkQLhlaDFzo5+UTu+/C4A49iLmHu7bbpsfW8iamonjEJ1s88/wdm7Yrou+FazbxY7719UNGh96EUMa8QbsG Bf9K5rDWhJpq8XTxakXRuTM6HiJDSmERbIWfyfRMfscXJPcRyTL6YyGNZxqkYSAQdB04t89/1O/w1cDnyilFU="
IMAGE_URL = "https://drive.google.com/uc?export=view&id=1AbCdEfGhIjKlMnOpQrStUvWxYz"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

pending_answers = {}

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()

    for event in body["events"]:
        user_id = event["source"]["userId"]

        if event["type"] == "follow":
            push_image(user_id, IMAGE_URL)
            push_text(user_id, "この画像を見て答えとなる写真を送ってください！")

        elif event["type"] == "message" and event["message"]["type"] == "image":
            message_id = event["message"]["id"]
            filename = save_image_from_line(message_id)
            pending_answers[user_id] = filename
            push_text(user_id, "写真を受け取りました。判定結果をお待ちください。")

    return "OK"

@app.route("/admin")
def admin_panel():
    return render_template("judge.html", answers=pending_answers)

@app.route("/judge")
def judge():
    user_id = request.args.get("user_id")
    result = request.args.get("result")

    if result == "correct":
        push_text(user_id, "正解！")
    else:
        push_text(user_id, "不正解。もう一度考えてみよう！")

    pending_answers.pop(user_id, None)
    return redirect("/admin")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def push_text(user_id, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {"to": user_id, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=data)

def push_image(user_id, image_url):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [{
            "type": "image",
            "originalContentUrl": image_url,
            "previewImageUrl": image_url
        }]
    }
    requests.post(url, headers=headers, json=data)

def save_image_from_line(message_id):
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    r = requests.get(url, headers=headers, stream=True)
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    return filename

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
