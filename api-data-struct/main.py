import os
from dotenv import load_dotenv
from rich import print

import dataclasses
from notion_client import Client
from time import sleep

# 実装した構造化スクリプト
import notion_st

if __name__ == "__main__":
    database_id = "10f2085cf70a4c939b2710e883eb161a"

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
    notion.pages.create(**post_data)

    sleep(1)
    print(post_data)
