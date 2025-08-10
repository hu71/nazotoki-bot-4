from flask import Flask, request, abort, render_template, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage, ImageSendMessage, FollowEvent
import os
from datetime import datetime

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

PUZZLE_IMAGE_URL = "https://drive.google.com/uc?export=view&id=1GhjyvsaWP23x_wdz7n-nSqq5cziFcf1U"

received_images = []

@app.route("/")
def index():
    return "LINE Bot is running."

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="謎解きに参加してくれてありがとう！"),
            TextSendMessage(text="それでは問題です。"),
            ImageSendMessage(original_content_url=PUZZLE_IMAGE_URL, preview_image_url=PUZZLE_IMAGE_URL)
        ]
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    message_id = event.message.id
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    received_images.append({
        "user_id": user_id,
        "timestamp": timestamp,
        "image_id": message_id,
    })

@app.route("/judge", methods=["GET", "POST"])
def judge():
    global received_images

    if request.method == "POST":
        image_id = request.form.get("image_id")
        user_id = request.form.get("user_id")
        judge = request.form.get("judge")

        if not image_id or not user_id or judge not in ("correct", "wrong"):
            return "Invalid input", 400

        text = "正解！" if judge == "correct" else "残念。もう一度考えてみよう！"

        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=text))
        except Exception as e:
            return f"Failed to send message: {str(e)}", 500

        received_images = [img for img in received_images if img["image_id"] != image_id]

        return redirect(url_for("judge"))

    return render_template("judge.html", images=received_images)

if __name__ == "__main__":
    # Renderでは不要なのでコメントアウトか削除でOK
    # app.run(debug=True, port=5000)
    pass

