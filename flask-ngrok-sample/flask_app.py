#!/usr/bin/env python3

import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request


def initFlaskApp(flask_app):
    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        return handler.handle(request)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from configparser import ConfigParser
    from slack_bolt import App
    from slack_bolt.adapter.flask import SlackRequestHandler

    from app_handler import SlackAppController  # 自作クラス

    # 設定情報をロード
    config = ConfigParser()
    config.read("config.ini", encoding="utf-8")
    # 秘密情報をロード
    load_dotenv()

    # ロードした情報を格納
    access_token = os.environ.get("SLACK_ACCESS_TOKEN")
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

    # インスタンス生成
    slack_app = App(signing_secret=signing_secret, token=access_token)
    handler = SlackRequestHandler(slack_app)
    slack_controller = SlackAppController(slack_app, handler)

    # Flaskを初期化
    flask_app = Flask(__name__)
    initFlaskApp(flask_app)

    # Flaskをslack_controllerで実行
    slack_controller.runFlask(flask_app)
