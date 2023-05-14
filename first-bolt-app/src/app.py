# 差し当たっての実装

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
# GPT-3.5-turbo
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    # System メッセージテンプレート
    SystemMessagePromptTemplate,
    # assistant メッセージテンプレート
    # AIMessagePromptTemplate,
    # user メッセージテンプレート
    HumanMessagePromptTemplate,
)
# from langchain.schema import (
#     # それぞれ GPT-3.5-turbo API の assistant, user, system role に対応
#     # AIMessage,
#     # HumanMessage,
#     # SystemMessage
# )

# 環境変数を設定
load_dotenv()

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# モデル作成
llm = ChatOpenAI(temperature=0, openai_api_key=os.environ.get("OPEN_API_KEY"))

# 日本語で ChatGPT っぽく丁寧に説明させる
system_message_prompt = SystemMessagePromptTemplate.from_template(
    "You are an assistant who thinks step by step and includes a thought path in your response. Your answers are in Japanese."
    )
# ユーザーからの入力
human_template = "{text}"
# User role のテンプレートに
message_prompt = HumanMessagePromptTemplate.from_template(human_template)

# ひとつのChatTemplateに
chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, message_prompt])
chat_prompt.input_variables = ['text']

# カスタムプロンプトを入れてchain 化
chain = LLMChain(llm=llm, prompt=chat_prompt)

# 'hello' を含むメッセージをリッスンします
# @app.message("hello")
# def message_hello(message, say):
#     # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
#     say(
#         blocks=[
#             {
#                 "type": "section",
#                 "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
#                 "accessory": {
#                     "type": "button",
#                     "text": {"type": "plain_text", "text":"Click Me"},
#                     "action_id": "button_click"
#                 }
#             }
#         ],
#         text=f"Hey there <@{message['user']}>!"
#     )


# メンションされた時


@app.event("message")
def handle_message_events(body, say):
    # メンションの内容を取得
    text = body['event']['text']
    say(text='回答を生成しています。しばらくお待ちください。')
    # LLMを動作させてチャンネルで発言
    say(chain.run(text=text))

# @app.action("button_click")
# def action_button_click(body, ack, say):
#     # アクションを確認したことを即時で応答します
#     ack()
#     # チャンネルにメッセージを投稿します
#     say(f"<@{body['user']['id']}> clicked the button")


# アプリを起動します


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()