import os
import re
from notion_client import Client as NotionClient
from notion_client.api_endpoints import BlocksChildrenEndpoint


class Gijiroku:
    def __init__(self):
        # Notion Client (https://github.com/ramnes/notion-sdk-py/tree/main)
        # タイムアウトを60から90秒に変更
        self.notion_client = NotionClient(auth=os.environ.get("NOTION_TOKEN"), timeout_ms=900_00)
        # blockを取得するためのエンドポイント
        self.endpoint = BlocksChildrenEndpoint(self.notion_client)
        # 議事録ページのID
        self.gijiroku_page_id = "0d1661a7710c4bc892b590b5df7faea9"

    # 「第○○回...」の一覧を取得
    def gijiroku_list(self):
        gijiroku = self.endpoint.list(self.gijiroku_page_id)

        pattern = '\d{4}-\d{2}-\d{2}'
        dict = {}
        for block in gijiroku["results"]:
            if block.get("heading_1"):
                p_text = self._get_text_from_heading(block, "1")
                # 一部を置換
                val = p_text.replace("年", "-").replace("月", "-").replace("日", "")
                # valueを抽出 ex. 2023-06-19
                re_val = re.search(pattern, val)
                if re_val:
                    dict[p_text] = re_val.group()

        return dict

    # 「議事録をまとめてください」のセレクトボックス用のblockを返す
    def gijiroku_select_block(self):
        gijiroku_options = []

        # 「第○○回...」の一覧を取得
        for k, v in self.gijiroku_list().items():
            gijiroku_options.append({"text": {"type": "plain_text", "text": k}, "value": v})

        return [
            {
                "type": "section",
                "block_id": "gijiroku_select",
                "text": {"type": "mrkdwn", "text": "どの回の議事録をまとめますか？"},
                "accessory": {
                    "action_id": "gijiroku_select_option",
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                    "options": gijiroku_options,
                },
            }
        ]

    # 議事メモの内容を取得する
    # 引数は取得対象の回
    def gijiroku_contents(self, target):
        gijiroku = self.endpoint.list(self.gijiroku_page_id)

        body = []
        for block in gijiroku["results"]:
            if block.get("heading_1"):
                if target in self._get_text_from_heading(block, "1"):
                    for block2 in self.endpoint.list(block["id"])["results"]:
                        if "議事メモ" in self._get_text_from_heading(block2, "2"):
                            self._get_text_recursively(body, block2)
        return body

    # heading_1, heading_2(dict型)からplain_textを取得する
    def _get_text_from_heading(self, block, level):
        if block.get("heading_" + level):
            body = block["heading_" + level]["rich_text"][0]["plain_text"]
            return body
        return ""

    # 自要素のplain_textを取得
    # その後,再帰的に子要素のplain_textを取得
    # bodyはリストなので参照渡しとなる
    def _get_text_recursively(self, body, block):
        for content in self.endpoint.list(block["id"])["results"]:
            txt = self._get_text_from_list_item(content)
            if txt:
                body.append(txt)
            if content["has_children"]:
                self._get_text_recursively(body, content)

    # child_block(dict型)からplain_textを取得する
    def _get_text_from_list_item(self, block):
        for item in ["numbered_list_item", "bulleted_list_item"]:
            if block.get(item):
                rich_text = block[item]["rich_text"]
                if rich_text:
                    # 全角スペースを削除
                    return rich_text[0]["plain_text"].replace("\u3000", " ")
