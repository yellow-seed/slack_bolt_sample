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

    create_page = notion_st.CreatePageInDb_ST(
        parent=notion_st.DbParent_ST(database_id),
        properties={  # ここはNotionの表によって変わるので、補助が出せない…
            "userid": notion_st.PageTitle_ST(
                [
                    notion_st.RichText_ST(
                        notion_st.Text_ST("abcdefg"),
                        notion_st.PageAnnotations_ST(italic=True, color=notion_st.Color_Const.purple_background),
                    )
                ]
            ),
            "活動報告": notion_st.PageText_ST(
                [
                    notion_st.RichText_ST(
                        notion_st.Text_ST("5Q-11"),
                        notion_st.PageAnnotations_ST(italic=True, color=notion_st.Color_Const.purple_background),
                    )
                ]
            ),
            # "タグ": notion_st.PageMultiSelect_ST(
            #     [
            #         notion_st.NewSelect_ST(
            #             name="新規",
            #             color=notion_st.Color_Const.orange,
            #         )
            #     ]
            # ),
            "内容": notion_st.PageText_ST(
                [
                    notion_st.RichText_ST(
                        notion_st.Text_ST("投稿テスト"),
                    )
                ]
            ),
        },
    )
    post_data = dataclasses.asdict(create_page)
    notion.pages.create(**post_data)

    sleep(1)

    response_dict = notion.databases.query(**{"database_id": database_id})
    db_query_res = notion_st.purseDbQueryRes(response_dict)
    print(db_query_res.results[0].properties)

    page_text = notion_st.pursePageTitle(db_query_res.results[0].properties["userid"])
    page_title = notion_st.pursePageText(db_query_res.results[0].properties["活動報告"])
    page_multi_select = notion_st.pursePageMultiSelect(db_query_res.results[0].properties["タグ"])

    print(page_multi_select.multi_select[0].name, page_multi_select.multi_select[0].id, page_multi_select.multi_select[0].color)
