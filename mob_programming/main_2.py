from main_1 import app, select_block, chain, notion, print


@app.event("app_mention")
def command_handler(body, say):
    # メンションの内容を取得
    mention_text = body["event"]["text"]
    if "マンスリーレビューをまとめてください" in mention_text:
        say(blocks=select_block)
    # LLMを動作させてチャンネルで発言
    say(chain.run(text=mention_text))


def fetch_records_for_week(semester=None, week=None):
    filter_obj = {
        "and": [
            {"property": "活動報告", "rich_text": {"contains": "1Q-05"}},
            {"property": "タグ", "multi_select": {"does_not_contain": "来週の活動と成果の予定"}},
            {"property": "タグ", "multi_select": {"contains": "今週の活動と成果の実績"}},
        ]
    }

    # filter_obj = {
    #     "or": [
    #         {"property": "活動報告", "rich_text": {"contains": "1Q-05"}},
    #         # {"property": "活動報告", "rich_text": {"contains": "1Q-06"}},
    #         # {"property": "活動報告", "rich_text": {"contains": "1Q-07"}},
    #         {"property": "活動報告", "rich_text": {"contains": "1Q-08"}},
    #         {"property": "活動報告", "rich_text": {"contains": "1Q-09"}},
    #     ],
    #     "and": [
    #         {"property": "タグ", "multi_select": {"does_not_contain": "来週の活動と成果の予定"}},
    #     ],
    # }
    pages = notion.databases.query(**{"database_id": "01be2b6ddec849d199e6c4f555accc98", "filter": filter_obj})["results"]
    results = []
    # 各レコードに対して
    for page in pages:
        # すべてのプロパティを取得
        properties = page["properties"]

        # 対象期間絞り込みのために活動報告カラムの値を取得
        target_period = properties["活動報告"]["rich_text"][0]["plain_text"]
        page_semester, page_week = target_period.split("-")

        # レコードの学期と週が指定された学期と週と一致するか確認
        # if semester == page_semester and week == page_week:
        # 一致する場合、各プロパティの値を取得
        row = {}
        for name, prop in properties.items():
            # プロパティのタイプによって異なる形式の値が存在するため、それを判定
            if prop["type"] == "title":
                # タイトルプロパティの場合、テキストを取得
                value = prop["title"][0]["plain_text"]  # userid
            elif prop["type"] == "rich_text":
                # リッチテキストプロパティの場合、テキストを取得
                value = prop["rich_text"][0]["plain_text"]  # 内容, 活動報告
            elif prop["type"] == "multi_select":  # タグ
                # マルチセレクトプロパティの場合、選択されたオプションの名前をすべて取得
                value = ", ".join(option["name"] for option in prop["multi_select"])
            else:
                value = "Unsupported property type: " + prop["type"]
            row[name] = value
        results.append(row)

    return results


# MOB flask_app.runで書き換え
# アプリを起動します
if __name__ == "__main__":
    mention_text = (
        "-困ったときは学習が目的というところに立ち返って、学習に最適な進め方を行う。-たとえば、プロダクトの締め切りに追われたとしても、リソース効率が落ちるからという理由でモブプログラミングを軽視しない。プロダクトを作ることが目的にならないように注意を払う。-モブプロにおいては、実装を実際に行う時間と、いったん立ち止まって情報の整理や質疑応答を行う時間に分けて運用すると学習効果が高まります。"
    )
    print(chain.run(text=fetch_records_for_week("2023-06-10", "2023-06-10")))
    print(fetch_records_for_week("2023-06-10", "2023-06-10"))

    # SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
