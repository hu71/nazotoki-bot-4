from flask import Flask, request, abort, render_template, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, ImageMessage, TextMessage,
    TextSendMessage, ImageSendMessage
)
from datetime import datetime

app = Flask(__name__)

# アクセストークンとシークレットを直書き（必要に応じて書き換えてください）
LINE_CHANNEL_ACCESS_TOKEN = "00KCkQLhlaDFzo5+UTu+/C4A49iLmHu7bbpsfW8iamonjEJ1s88/wdm7Yrou+FazbxY7719UNGh96EUMa8QbsG Bf9K5rDWhJpq8XTxakXRuTM6HiJDSmERbIWfyfRMfscXJPcRyTL6YyGNZxqkYSAQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "6c12aedc292307f95ccd67e959973761"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleドライブの問題画像URL
PUZZLE_IMAGE_URL = "https://drive.google.com/uc?export=view&id=1GhjyvsaWP23x_wdz7n-nSqq5cziFcf1U"

# 判定用に受け取った画像の情報を保存
received_images = []


@app.route("/")
def index():
    return "LINE Bot is running."


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    print("callback received")
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


# 「2MB」と送ったら問題画像を送信
@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_text = event.message.text.strip()

    if user_text == "2MB":
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="それでは問題です。"),
                ImageSendMessage(
                    original_content_url=PUZZLE_IMAGE_URL,
                    preview_image_url=PUZZLE_IMAGE_URL
                )
            ]
        )
    else:
        # デバッグ用：オウム返し
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"あなたが送ったのは: {user_text}")
        )


# 画像が送られたら判定用に記録
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


# 主催者用の判定フォーム
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
    app.run(host="0.0.0.0", port=5000)
