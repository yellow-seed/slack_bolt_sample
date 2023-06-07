import logging
import os

from slack_bolt import App
from dotenv import load_dotenv

# 環境変数を設定
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

# 'hello' を含むメッセージをリッスンします
@app.message("hello")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    say("hello")


from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    payload = request.get_json()
    if 'challenge' in payload:
        # これはチャレンジリクエストです。アプリを確認するためにチャレンジ値で応答してください。
        # ref: https://qiita.com/masa_masa_ra/items/618779e698921cb53cec
        return payload['challenge']
    else:
        # これは通常のイベントです。SlackRequestHandlerで処理してください。
        return handler.handle(request)


# Only for local debug
if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))