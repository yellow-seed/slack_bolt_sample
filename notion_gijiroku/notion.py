import os
import re
from dotenv import load_dotenv
from notion_client import Client as NotionClient
from notion_client.api_endpoints import BlocksChildrenEndpoint

load_dotenv()
# Notion Client (https://github.com/ramnes/notion-sdk-py/tree/main)
# タイムアウトを60から90秒に変更
notion = NotionClient(auth=os.environ.get("NOTION_TOKEN"), timeout_ms=900_00)


# child_block(dict型)からplain_textを取得する
def _get_text_from_list_item(block):
    plain_text = ""
    for item in ["numbered_list_item", "bulleted_list_item"]:
        if block.get(item):
            rich_text = block[item]["rich_text"]
            if rich_text:
                plain_text = rich_text[0]["plain_text"]
                break

    # 全角スペースを削除
    return plain_text.replace("\u3000", " ")


# heading_1, heading_2(dict型)からplain_textを取得する
def _get_text_from_heading(block, level):
    if block.get("heading_" + level):
        body = block["heading_" + level]["rich_text"][0]["plain_text"]
        return body
    return ""


# 自要素のplain_textを取得
# その後,再帰的に子要素のplain_textを取得
# bodyは参照渡し
def get_text_recursively(body, block, endpoint=None):
    if not endpoint:
        endpoint = BlocksChildrenEndpoint(notion)

    for content in endpoint.list(block["id"])["results"]:
        txt = _get_text_from_list_item(content)
        if txt:
            body.append(txt)
        if content["has_children"]:
            get_text_recursively(body, content, endpoint)


# 議事録ページのID
PAGE_ID = "0d1661a7710c4bc892b590b5df7faea9"


# 議事メモの内容を取得する
# 引数は取得対象の回
def gijiroku_contents(target):
    body = []
    block_children = BlocksChildrenEndpoint(notion)
    gijiroku = block_children.list(PAGE_ID)

    for block in gijiroku["results"]:
        if block.get("heading_1"):
            if target in _get_text_from_heading(block, "1"):
                for block2 in block_children.list(block["id"])["results"]:
                    if "議事メモ" in _get_text_from_heading(block2, "2"):
                        get_text_recursively(body, block2, block_children)
    return body


# 「第○○回...」の一覧を取得
def gijiroku_list():
    pattern = '\d{4}-\d{2}-\d{2}'

    gijiroku = BlocksChildrenEndpoint(notion).list(PAGE_ID)
    dict = {}
    for block in gijiroku["results"]:
        if block.get("heading_1"):
            p_text = _get_text_from_heading(block, "1")
            # 一部を置換
            val = p_text.replace("年", "-").replace("月", "-").replace("日", "")
            # valueを抽出 ex. 2023-06-19
            re_val = re.search(pattern, val)
            if re_val:
                dict[p_text] = re_val.group()

    return dict


# 「議事録をまとめてください」のセレクトボックス用のblockを返す
# 戻り値をSlackAPIのsay関数のblocks引数に渡す
def gijiroku_select_block():
    gijiroku_options = []

    # 「第○○回...」の一覧を取得
    for k, v in gijiroku_list().items():
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