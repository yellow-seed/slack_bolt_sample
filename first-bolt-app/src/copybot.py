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
from tqdm import tqdm

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
        要約というのは、文章全体の中から重要なトピックを見つけ出し、そのトピックごとに要点をまとめ、エッセンスとなる情報だけに絞り込むことだよ。
        長い文章は要約とは言えないから注意してね。
            ＜ルール＞
            ・「活動内容と成果の実績」、「課題と解決策」、「できごと・気づき」の３つの大項目を立て、この大項目ごとに要約を記載すること（これ以外の項目は立てないこと）
            ・上記３つの各項目につき、３箇条ずつ箇条書きで要約を記載すること（４箇条以上は記載しないこと）
            ・一文につき各37文字以内とすること
            ・回答全体の総文字数は330文字以内とすること
            ・回答は12行以内とすること
            ・「今週の活動と成果の実績」という名前の項目は立てないこと

            回答作成に当たっては次の記載例を参考にすること。
            文字数や構成は下記記載例から大きく逸脱しないこと。
            ＜記載例＞
                【活動内容と成果の実績】
                ・モブプログラミングを実施し、APIの使い方を学んだ
                ・スクラム運営方針を決定し、スプリントの設計を行った
                ・マンスリーレビューの指摘事項について振り返りを行った
                【課題と解決策】
                ・スケジュール遅延が繰り返し生じている
                ・まだ悲鳴を上げることに抵抗感が残っている
                ・評価指標が未作成である
                【できごと・気づき】
                ・モブプロにより他のメンバーとの知見共有がスムーズになった
                ・輪読会での学びがスプリントの設計に活用できた
                ・スクラムの精神を学び失敗しても大丈夫な雰囲気の醸成ができた

            ＜以下の行から先が週報の内容。下記を要約すること。＞
            {weekly_reports}
        """
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        chat_prompt.input_variables = ["month", "weekly_reports"]

        chain = LLMChain(llm=llm, prompt=chat_prompt)

        return chain

    def register_listeners(self):
        @self.app.message(re.compile("(週報要約|マンスリーレビュー作って|たのむ|たのんだ)"))
        def message_hello(say):
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
        def target_month_select(body, ack, say):
            ack()

            month = body['actions'][0]['selected_option']['value']
            target_period_col = "活動報告"
            semesters = ["1Q"]  # ["2Q", "3Q", "4Q"]

            period_dict = {"4": [f"{i:02d}" for i in range(1, 5)],
                           "5": [f"{i:02d}" for i in range(5, 10)],
                           "6": [f"{i:02d}" for i in range(10, 15)],
                           "7": [f"{i:02d}" for i in range(15, 20)]}

            weeks = period_dict[month]

            say(f"了解。{month}月の週報をもとにマンスリーレビュー資料をまとめるね。少し待ってね。")

            # クライアントの初期化
            notion_api_key = os.environ.get("NOTION_API_KEY")
            table_id = "01be2b6ddec849d199e6c4f555accc98"
            client = NotionWeeklyReportFetcher(notion_api_key, table_id, target_period_col)

            summaries = []

            # 指定した学期と週のデータを１週間ずつ逐次抽出
            for semester in semesters:
                for week in tqdm(weeks):
                    weekly_reports = client.fetch_records_for_week(semester, week)

                    # 当該週のデータがない場合はスキップ
                    if weekly_reports == []:
                        continue

                    # 抽出した週のデータを要約
                    summary = self.chain.run(month=month, weekly_reports=weekly_reports)
                    summaries.append(summary)
                    print(summary)

            # すべての要約を結合して更に要約
            print('各週の内容から１か月分の要約を作成中...')
            concat_summary = ' '.join(summaries)
            monthly_report = self.chain.run(month=month, weekly_reports=concat_summary)
            say(monthly_report)
            print("Done!")

    def start(self):
        SocketModeHandler(self.app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    bot = CoPyBot()
    bot.start()
