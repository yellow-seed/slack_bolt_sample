from notion_client import Client


class NotionWeeklyReportFetcher:
    def __init__(self, api_key):
        self.notion_client = Client(auth=api_key)

    def preprocess(self, row_data):
        results = []
        for dic in row_data:
            if dic["タグ"] == "来週の活動と成果の予定" or dic["内容"] == "":
                continue
            new_dict = {key: dic[key].replace("\r", "").replace("\n", "") for key in dic if key not in ["活動報告", "userid"]}
            results.append(new_dict)
        return results

    def fetch_records_for_week(self, semester, week):
        # データベースからすべてのレコードを取得
        pages = self.notion_client.databases.query(
            database_id="01be2b6ddec849d199e6c4f555accc98")["results"]

        results = []
        # 各レコードに対して
        for page in pages:
            # すべてのプロパティを取得
            properties = page["properties"]

            # 対象期間絞り込みのために活動報告カラムの値を取得
            target_period = properties["活動報告"]["rich_text"][0]["plain_text"]
            page_semester, page_week = target_period.split("-")

            # レコードの学期と週が指定された学期と週と一致するか確認
            if semester == page_semester and week == page_week:
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

        return self.preprocess(results)
