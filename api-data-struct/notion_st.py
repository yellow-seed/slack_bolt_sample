#!/usr/bin/env python3

from dotenv import load_dotenv
from rich import print
import dataclasses
from typing import List

from notion_client import Client
from time import sleep


# ここから基本要素
# https://developers.notion.com/reference/rich-text#text
@dataclasses.dataclass(frozen=True)
class Text_ST:
    content: str
    link: str = None


# https://developers.notion.com/reference/rich-text#the-annotation-object (color)
@dataclasses.dataclass(frozen=True)
class Color_ST:
    blue: str = "blue"
    brown: str = "brown"
    gray: str = "gray"
    green: str = "green"
    orange: str = "orange"
    pink: str = "pink"
    purple: str = "purple"
    red: str = "red"
    yellow: str = "yellow"
    default: str = "default"
    blue_background: str = "blue_background"
    brown_background: str = "brown_background"
    gray_background: str = "gray_background"
    green_background: str = "green_background"
    orange_background: str = "orange_background"
    pink_background: str = "pink_background"
    purple_background: str = "purple_background"
    red_background: str = "red_background"
    yellow_background: str = "yellow_background"


# https://developers.notion.com/reference/rich-text#the-annotation-object
@dataclasses.dataclass(frozen=True)
class PageAnnotations_ST:
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: Color_ST = Color_ST.default


# https://developers.notion.com/reference/rich-text
@dataclasses.dataclass(frozen=True)
class RichText_ST:
    plain_text: str
    text: Text_ST
    annotations: PageAnnotations_ST
    href: str = None
    type: str = "text"


# ここまで基本要素
# ここから下はPageの要素
# 基本要素の組み合わせで成り立っている。
# https://developers.notion.com/reference/page-property-values#rich-text
@dataclasses.dataclass(frozen=True)
class PageText_ST:
    rich_text: List[RichText_ST]
    type: str = "rich_text"


# https://developers.notion.com/reference/page-property-values#title
@dataclasses.dataclass(frozen=True)
class PageTitle_ST:
    title: List[RichText_ST]
    id: str = "title"
    type: str = "title"


# https://developers.notion.com/reference/parent-object
@dataclasses.dataclass(frozen=True)
class PageParentDb_ST:
    database_id: str
    type: str = "database_id"


# https://developers.notion.com/reference/parent-object
@dataclasses.dataclass(frozen=True)
class PageParentPage_ST:
    page_id: str = None
    type: str = "page_id"


# https://developers.notion.com/reference/post-page
@dataclasses.dataclass(frozen=True)
class CreatePage_ST:
    parent: dict
    properties: dict  # https://developers.notion.com/reference/page-property-values


# https://developers.notion.com/reference/post-database-query
@dataclasses.dataclass(frozen=True)
class DbQueryRespResult_ST:
    object: str
    id: str
    created_time: str
    last_edited_time: str
    created_by: dict
    last_edited_by: dict
    cover: str
    icon: str
    parent: PageParentDb_ST
    archived: bool
    properties: dict
    url: str
    public_url: str


# https://developers.notion.com/reference/post-database-query
@dataclasses.dataclass(frozen=True)
class DbQueryResp_ST:
    object: str
    results: List[dict]
    next_cursor: str
    has_more: bool
    type: str
    page: dict


def pursePageText(page_text_dict: dict) -> PageText_ST:
    if "id" in page_text_dict:
        del page_text_dict["id"]

    page_text = PageText_ST(**page_text_dict)
    rich_texts = []
    for rich_text_elem in page_text.rich_text:
        rich_texts.append(purseRichText(rich_text_elem))

    ret = PageText_ST(rich_texts)
    return ret


def purseRichText(rich_text_dict: dict) -> RichText_ST:
    rich_text = RichText_ST(**rich_text_dict)
    plain_text = rich_text.plain_text
    text = Text_ST(**rich_text.text)
    annotations = PageAnnotations_ST(**rich_text.annotations)

    ret = RichText_ST(plain_text, text, annotations)
    return ret


if __name__ == "__main__":
    import os

    database_id = "10f2085cf70a4c939b2710e883eb161a"

    # 秘密情報をロード
    load_dotenv()
    api_key = os.environ.get("NOTION_API_KEY")
    notion = Client(auth=api_key)

    page_parent = PageParentDb_ST(database_id=database_id, type="database_id")
    page_parent_dict = dataclasses.asdict(page_parent)

    page_title = PageTitle_ST(
        [
            RichText_ST(plain_text="test", text=Text_ST("test"), annotations=PageAnnotations_ST()),
        ]
    )
    page_title_dict = dataclasses.asdict(page_title)

    page_text = PageText_ST(
        [
            RichText_ST(plain_text="テキストテスト", text=Text_ST("テキストテスト"), annotations=PageAnnotations_ST(color=Color_ST.red_background)),
        ]
    )
    page_text_dict = dataclasses.asdict(page_text)

    page_text = pursePageText(page_text_dict)
    print(page_text.rich_text[0].annotations.color)

    page_properties = {"タイトルヘッダー": page_title_dict, "テキストヘッダー": page_text_dict}
    create_page_struct = CreatePage_ST(page_parent, page_properties)
    post_data = dataclasses.asdict(create_page_struct)
    # print(post_data)

    # notion.pages.create(**post_data)
    # sleep(1)

    # response_dict = notion.databases.query(**{"database_id": database_id})
    # response = DbQueryResp_ST(**response_dict)
    # resp_result_dict = response.results[0]
    # resp_result = DbQueryRespResult_ST(**resp_result_dict)
    # print(resp_result)
    # print(resp_result.parent.database_id)

    # result_dict = response_dict["results"][0]
    # page_parent_dict = result_dict["parent"]
    # page_properties_dict = result_dict["properties"]
    # page_text_dict = page_properties_dict["テキストヘッダー"]

    # page_parent = PageParentDb_ST(**page_parent_dict)
    # print(page_parent.database_id)
    # print(page_parent.type)

    # page_title = PageTitle_ST(**page_properties_dict["タイトルヘッダー"])
    # page_text = pursePageText(page_text_dict)
    # print(page_text.rich_text[0].annotations.color)
