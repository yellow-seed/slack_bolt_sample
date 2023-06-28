#!/usr/bin/env python3

import os
import sys

from dotenv import load_dotenv
from rich import print

import dataclasses
from notion_client import Client
from time import sleep

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../api-data-struct")

if __name__ == "__main__":
    # 実装した構造化スクリプト
    import notion_st

    database_id = "01be2b6ddec849d199e6c4f555accc98"

    # 秘密情報をロード
    load_dotenv()
    api_key = os.environ.get("NOTION_API_KEY")
    notion = Client(auth=api_key)

    db_parent = notion_st.DbParent_ST(database_id)
    page_title = notion_st.PageTitle_ST(
        [
            notion_st.RichText_ST(text=notion_st.Text_ST("タイトル名")),
        ]
    )
    page_text = notion_st.PageText_ST(
        [
            notion_st.RichText_ST(plain_text="テキストテスト", text=notion_st.Text_ST("テキストテスト"), annotations=notion_st.PageAnnotations_ST(color=notion_st.Color_Const.red_background)),
        ]
    )

    create_page = notion_st.CreatePageInDb_ST(db_parent, {"タイトルヘッダー": page_title, "テキストヘッダー": page_text})  # ここはNotionの表によって変わるので、補助が出せない…
    post_data = dataclasses.asdict(create_page)
    # notion.pages.create(**post_data)

    sleep(1)

    response_dict = notion.databases.query(**{"database_id": database_id})
    db_query_res = notion_st.purseDbQueryRes(response_dict)
    print(db_query_res.results[0].properties)

    page_text = notion_st.pursePageTitle(db_query_res.results[0].properties["userid"])
    page_title = notion_st.pursePageText(db_query_res.results[0].properties["活動報告"])
    page_multi_select = notion_st.pursePageMultiSelect(db_query_res.results[0].properties["タグ"])

    print(page_multi_select.multi_select[0].color)
