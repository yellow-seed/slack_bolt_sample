#!/usr/bin/env python3

from rich import print
from notion_client import Client
from time import sleep


class DbContents(object):
    def __init__(self, api_key):
        self.notion = Client(auth=api_key)
        self.db_rows = []
        self.db_contents = []

    def pull(self, database_id):
        self.database_id = database_id
        self.db_rows = []
        self.db_contents = []
        database = self.notion.databases.query(**{"database_id": database_id})
        for result_dict in database["results"]:
            if result_dict["object"] != "page":
                continue
            page_id = result_dict["id"]
            db_row_cells = NotionRowCells(page_id)
            db_row_contents = {}

            for key, values in result_dict["properties"].items():
                cell_type = values["type"]
                if cell_type == "multi_select":
                    notion_cell = MultiSelect(values[cell_type])
                elif cell_type == "rich_text":
                    notion_cell = RichText(values[cell_type])
                elif cell_type == "title":
                    notion_cell = Title(values[cell_type])
                elif cell_type == "number":
                    notion_cell = Number(values[cell_type])
                elif cell_type == "select":
                    notion_cell = Select(values[cell_type])
                elif cell_type == "date":
                    notion_cell = NotionDate(values[cell_type])
                elif cell_type == "people":
                    notion_cell = People(values[cell_type])
                else:
                    print("cell_type:", cell_type, "が実装されていません。")
                    print("詳細:", values)
                    notion_cell = NotionCell(values[cell_type])
                db_row_cells.addCell(key, notion_cell)
                db_row_contents[key] = notion_cell.getContent()

            self.db_rows.append(db_row_cells)
            self.db_contents.append(db_row_contents)

        return self.db_contents

    def append(self, dict_row):
        if self.db_contents == []:
            print("pullしてからappendしてください")
            exit()

        propertes = {}
        for key, cell in self.db_rows[0].items():
            content = dict_row[key]
            propertes[key] = cell.makeProperty(content)

        self.notion.pages.create(**{"parent": {"database_id": self.database_id}, "properties": propertes})

    # appendしたものを消すには、再度pullが必要
    def delete(self, key, value):
        for db_row_cells in self.db_rows:
            page_id = db_row_cells.match(key, value)
            if page_id != None:
                self.notion.blocks.delete(**{"block_id": page_id})
                sleep(0.5)


class NotionRowCells(object):
    def __init__(self, page_id) -> None:
        self.cell_dict = {}
        self.page_id = page_id

    def addCell(self, key, notion_cell):
        self.cell_dict[key] = notion_cell

    def items(self):
        return self.cell_dict.items()

    def match(self, key, value):
        if self.cell_dict[key].getContent() == value:
            ret = self.page_id
        else:
            ret = None
        return ret


class NotionCell(object):
    def __init__(self, cell_type_value) -> None:
        if cell_type_value != [] and cell_type_value != None:
            self.dict = cell_type_value
        else:
            self.dict = None

    def getContent(self):
        return None

    def makeProperty(self):
        return None


class MultiSelect(NotionCell):
    def getContent(self):
        if self.dict != None:
            ret = [selector["name"] for selector in self.dict]
        else:
            ret = None
        return ret

    def makeProperty(self, content):
        property_value = {"multi_select": [{"name": content}]}
        return property_value


class RichText(NotionCell):
    def getContent(self):
        if self.dict != None:
            ret = self.dict[0]["plain_text"]
        else:
            ret = None
        return ret

    def makeProperty(self, content):
        property_value = {"rich_text": [{"text": {"content": content}}]}
        return property_value


class Title(NotionCell):
    def getContent(self):
        if self.dict != None:
            ret = self.dict[0]["plain_text"]
        else:
            ret = None
        return ret

    def makeProperty(self, content):
        property_value = {"title": [{"text": {"content": content}}]}
        return property_value


class Number(NotionCell):
    def getContent(self):
        if self.dict != None:
            ret = self.dict  # 数値
        else:
            ret = None
        return ret

    def makeProperty(self, content):
        property_value = {"number": content}
        return property_value


class Select(NotionCell):
    def getContent(self):
        if self.dict != None:
            ret = self.dict["name"]
        else:
            ret = None
        return ret

    def makeProperty(self, content):
        property_value = {"select": {"name": content}}
        return property_value


class NotionDate(NotionCell):
    def getContent(self):
        if self.dict != None:
            ret = self.dict["start"]
        else:
            ret = None
        return ret

    def makeProperty(self, content):
        property_value = {"date": {"start": content.replace("/", "-")}}
        return property_value


class People(NotionCell):
    def getContent(self):
        if self.dict != None:
            ret = [person["name"] for person in self.dict]
        else:
            ret = None
        return ret

    def makeProperty(self, content):
        if content != None:
            property_value = {"people": [{"name": content}]}
        else:
            property_value = None
        return property_value


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from configparser import ConfigParser

    # 秘密情報をロード
    load_dotenv()
    api_key = os.environ.get("NOTION_API_KEY")

    # 設定値をロード
    config = ConfigParser()
    config.read("/workspaces/slack_bolt_sample/notion_db_sample/config.ini", encoding="utf-8")
    table_id = config.get("Database", "weekly_report_id")

    # データを取得
    db_contents = DbContents(api_key)
    rows = db_contents.pull(table_id)
    print(rows[0])

    # データを追加
    sleep(1)
    db_contents.append({"タグ": "来週の活動と成果の予定", "内容": "スクラムの勉強つづき", "活動報告": "1Q-03", "userid": "test_user"})

    # データを削除
    sleep(1)
    db_contents.delete("userid", "test_user")
