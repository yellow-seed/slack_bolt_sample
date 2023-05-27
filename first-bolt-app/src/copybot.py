import os
import re

from dotenv import load_dotenv
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from notion_fetcher import NotionWeeklyReportFetcher
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()


class CoPyBot:
    def __init__(self):
        self.app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

        llm = ChatOpenAI(temperature=0,
                         openai_api_key=os.environ.get("OPENAI_API_KEY"),
                         model_name="gpt-3.5-turbo")
        self.chain = self.create_chain(llm)
        self.register_listeners()

    def create_chain(self, llm):
        system_template = """
        You are an assistant who thinks step by step and includes a thought path in your response.
        Your answers are in Japanese.
        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_template = """
        {month}月の週報の内容を以下のルールに従って要約してね。
            【ルール】
            ・「活動内容」、「課題」、「気づき」の３つの項目に分けて記載すること
            ・各項目ごとに３つの内容を箇条書きで記載すること
            ・一文は短く端的な文章とすること
            ・大学教授に説明するためにアカデミックな文面で表記すること

            【以下の行から先が週報の内容】
            {weekly_reports}
        """
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        chat_prompt.input_variables = ["month", "weekly_reports"]

        chain = LLMChain(llm=llm, prompt=chat_prompt)

        return chain

    def register_listeners(self):
        @self.app.message(re.compile("(週報要約|マンスリーレビュー作って|たのむ|たのんだ)"))
        def message_hello(message, say):
            text = "こんにちは。co-py-bot だよ。\nマンスリーレビューを作成したい対象月を選んでね。"
            say(
                blocks=[
                    {
                        "type": "section",
                        "block_id": "section678",
                        "text": {"type": "mrkdwn", "text": text},
                        "accessory": {
                            "action_id": "select_month",
                            "type": "static_select",
                            "placeholder": {"type": "plain_text", "text": "対象月を選択"},
                            "options": [{"text": {"type": "plain_text", "text": f"{month}月"},
                                         "value": f"{month}"} for month in range(1, 13)],
                        },
                    }
                ],
                text=text,
            )

        @self.app.action("select_month")
        def action_button_click(body, ack, say):
            month = body['actions'][0]['selected_option']['value']

            target_period_col = "活動報告"
            # 抽出したい学期をリストで指定
            semesters = ["1Q"]  # ["2Q", "3Q", "4Q"]
            # 抽出したい週数をリストで指定

            """
            本当は以下のように対象期間全て抜き出したいがトークン上限に引っかかる。
            period_dict = {"4": [f"{i:02d}" for i in range(1, 5)],
                           "5": [f"{i:02d}" for i in range(5, 10)],
                           "6": [f"{i:02d}" for i in range(10, 15)],
                           "7": [f"{i:02d}" for i in range(15, 20)]}
            """
            # 上記のため試行版ということでとりあえず一部だけを使う形。ここは要改善
            period_dict = {"4": ["03"],
                           "5": ["08"],
                           "6": ["13"],
                           "7": ["18"]}

            weeks = period_dict[month]

            # クライアントの初期化
            notion_api_key = os.environ.get("NOTION_API_KEY")
            table_id = "01be2b6ddec849d199e6c4f555accc98"
            client = NotionWeeklyReportFetcher(notion_api_key, table_id, target_period_col)

            # 指定した学期と週のデータを抽出
            weekly_reports = client.fetch_pages(semesters, weeks)

            ack()
            say(f"了解。{month}月の週報をもとにマンスリーレビュー資料をまとめるね。少し待ってね。")
            say(self.chain.run(month=month, weekly_reports=weekly_reports))

    def start(self):
        SocketModeHandler(self.app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    bot = CoPyBot()
    bot.start()
