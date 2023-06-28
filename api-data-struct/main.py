#!/usr/bin/env python3

import os
import sys

from dotenv import load_dotenv
from rich import print

from notion_client import Client

# from time import sleep

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../api-data-struct")

if __name__ == "__main__":
    # 実装した構造化スクリプト
    import notion_st

    INDEX_ZERO = 0
    database_id = "01be2b6ddec849d199e6c4f555accc98"

    # 秘密情報をロード
    load_dotenv()
    api_key = os.environ.get("NOTION_API_KEY")
    notion = Client(auth=api_key)

    response_dict = notion.databases.query(**{"database_id": database_id})
    db_query_res = notion_st.purseDbQueryRes(response_dict)
    print(db_query_res.results[0].archived)

    user_id = notion_st.pursePageTitle(db_query_res.results[0].properties["userid"])
    quarter_num = notion_st.pursePageText(db_query_res.results[0].properties["活動報告"])
    tag = notion_st.pursePageMultiSelect(db_query_res.results[0].properties["タグ"])
    contents = notion_st.pursePageText(db_query_res.results[0].properties["内容"])

    print(user_id.title[INDEX_ZERO].text.content)
    print(tag.multi_select[INDEX_ZERO])
    print(tag.multi_select[INDEX_ZERO].name)

    tag = notion_st.pursePagePropaty(db_query_res.results[0].properties["タグ"])
