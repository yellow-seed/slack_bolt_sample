import os
import re
from dotenv import load_dotenv
from notion_client import Client as NotionClient
from notion_client.api_endpoints import BlocksChildrenEndpoint

load_dotenv()
notion = NotionClient(auth=os.environ.get("NOTION_TOKEN"))


# child_block(dict型)からplain_textを取得する
def get_text_from_list_item(block):
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
def get_text_from_heading(block, level):
    if block.get("heading_" + level):
        body = block["heading_" + level]["rich_text"][0]["plain_text"]
        return body
    return ""


# 議事録ページのID
PAGE_ID = "0d1661a7710c4bc892b590b5df7faea9"


# 議事メモの内容を取得する
# 色々とあきらめたコード
def gijiroku_contents(target):
    body = []
    block_children = BlocksChildrenEndpoint(notion)
    gijiroku = block_children.list(PAGE_ID)

    for block in gijiroku["results"]:
        if block.get("heading_1"):
            if target in get_text_from_heading(block, "1"):
                for block2 in block_children.list(block["id"])["results"]:
                    if "議事メモ" in get_text_from_heading(block2, "2"):
                        for block3 in block_children.list(block2["id"])["results"]:
                            txt3 = get_text_from_list_item(block3)
                            if txt3:
                                body.append(txt3)
                            if block3["has_children"]:
                                for block4 in block_children.list(block3["id"])["results"]:
                                    txt4 = get_text_from_list_item(block4)
                                    if txt4:
                                        body.append(txt4)
                                    if block4["has_children"]:
                                        for block5 in block_children.list(block4["id"])["results"]:
                                            txt5 = get_text_from_list_item(block5)
                                            if txt5:
                                                body.append(txt5)
                                            if block5["has_children"]:
                                                for block6 in block_children.list(block5["id"])["results"]:
                                                    txt6 = get_text_from_list_item(block6)
                                                    if txt6:
                                                        body.append(txt6)
    return body


# 「第○○回...」の一覧を取得
def gijiroku_list():
    pattern = '\d{4}-\d{2}-\d{2}'

    gijiroku = BlocksChildrenEndpoint(notion).list(PAGE_ID)
    dict = {}
    for block in gijiroku["results"]:
        if block.get("heading_1"):
            p_text = get_text_from_heading(block, "1")
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