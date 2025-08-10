from flask import Flask, request, abort, render_template, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, ImageMessage, TextSendMessage, ImageSendMessage, FollowEvent
)
from datetime import datetime

app = Flask(__name__)

# ここにあなたのアクセストークンとシークレットを直書きしてください
LINE_CHANNEL_ACCESS_TOKEN = "00KCkQLhlaDFzo5+UTu+/C4A49iLmHu7bbpsfW8iamonjEJ1s88/wdm7Yrou+FazbxY7719UNGh96EUMa8QbsG Bf9K5rDWhJpq8XTxakXRuTM6HiJDSmERbIWfyfRMfscXJPcRyTL6YyGNZxqkYSAQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "6c12aedc292307f95ccd67e959973761"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleドライブ画像URL（共有リンクID部分を変更してください）
PUZZLE_IMAGE_URL = "https://drive.google.com/uc?export=view&id=1GhjyvsaWP23x_wdz7n-nSqq5cziFcf1U"

received_images = []

@app.route("/")
def index():
    return "LINE Bot is running."

@app.route("/callback", methods=['POST'])
def callback():
    print("callback received")
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    print(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature error")
        abort(400)
    except Exception as e:
        print(f"Exception: {e}")
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    print(f"Follow event from user: {user_id}")

    try:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="謎解きに参加してくれてありがとう！"),
                TextSendMessage(text="それでは問題です。"),
                ImageSendMessage(original_content_url=PUZZLE_IMAGE_URL, preview_image_url=PUZZLE_IMAGE_URL)
            ]
        )
    except Exception as e:
        print(f"Failed to reply FollowEvent: {e}")

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    message_id = event.message.id
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Received image from user {user_id} at {timestamp}, message id: {message_id}")

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
