from notion_client import Client


class NotionWeeklyReportFetcher:
    def __init__(self, api_key, table_id, activity_report_column):
        self.notion = Client(auth=api_key)
        self.table_id = table_id
        self.activity_report_column = activity_report_column

    def fetch_pages(self, semesters, weeks):
        # データベースからすべてのレコードを取得
        pages = self.notion.databases.query(database_id=self.table_id)["results"]

        results = []

        # 各レコードに対して
        for page in pages:
            # すべてのプロパティを取得
            properties = page["properties"]

            # 対象期間絞り込みのために活動報告カラムの値を取得
            activity_report_value = properties[self.activity_report_column]["rich_text"][0]["plain_text"]
            semester, week = activity_report_value.split('-')

            # 活動報告カラムの値が指定する値に該当するかどうかを判定
            if semester in semesters and week in weeks:
                # 指定する値に該当する場合、各プロパティの値を取得
                row = {}
                for name, prop in properties.items():
                    # プロパティのタイプによって異なる形式の値が存在するため、それを判定
                    if prop["type"] == "title":
                        # タイトルプロパティの場合、テキストを取得
                        value = prop["title"][0]["plain_text"]
                    elif prop["type"] == "rich_text":
                        # リッチテキストプロパティの場合、テキストを取得
                        value = prop["rich_text"][0]["plain_text"]
                    elif prop["type"] == "multi_select":
                        # マルチセレクトプロパティの場合、選択されたオプションの名前をすべて取得
                        value = ", ".join(option["name"] for option in prop["multi_select"])
                    else:
                        value = "Unsupported property type: " + prop["type"]
                    row[name] = value
                results.append(row)

        return results
