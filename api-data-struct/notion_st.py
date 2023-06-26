#!/usr/bin/env python3

from dotenv import load_dotenv
from rich import print
import dataclasses

from notion_client import Client
from time import sleep


# ここから基本要素
# https://developers.notion.com/reference/rich-text#text
@dataclasses.dataclass(frozen=True)
class Text_ST:
    content: str
    link: str = None


# https://developers.notion.com/reference/rich-text#the-annotation-object (color)
# 定数であることを_Constで表現している。
# もっと良い方法があれば教えてください。
@dataclasses.dataclass(frozen=True)
class Color_Const:
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
    color: Color_Const = Color_Const.default


# https://developers.notion.com/reference/rich-text
@dataclasses.dataclass(frozen=True)
class RichText_ST:
    text: Text_ST
    annotations: PageAnnotations_ST = PageAnnotations_ST()
    plain_text: str = "undefined"
    href: str = None
    type: str = "text"


# ここまで基本要素
# ここから下はPageの要素
# 基本要素の組み合わせで成り立っている。
# https://developers.notion.com/reference/page-property-values#rich-text
@dataclasses.dataclass(frozen=True)
class PageText_ST:
    rich_text: list[RichText_ST]
    type: str = "rich_text"
    id: str = "undefined"


# https://developers.notion.com/reference/page-property-values#title
@dataclasses.dataclass(frozen=True)
class PageTitle_ST:
    title: list[RichText_ST]
    id: str = "title"
    type: str = "title"


# https://developers.notion.com/reference/parent-object#database-parent
@dataclasses.dataclass(frozen=True)
class DbParent_ST:
    database_id: str
    type: str = "database_id"


# https://developers.notion.com/reference/parent-object#page-parent
@dataclasses.dataclass(frozen=True)
class PageParent_ST:
    page_id: str
    type: str = "page_id"


# https://developers.notion.com/reference/property-object
@dataclasses.dataclass(frozen=True)
class PageProperties_ST(object):
    def __init__(self, headers: list, contents: list) -> None:
        self.__dict = {}
        for key, value in zip(headers, contents):
            self.__dict[key] = value

    # プロパティの値を取り出すメソッドを定義する
    @property
    def dict(self):
        return self.__dict


# https://developers.notion.com/reference/post-page
@dataclasses.dataclass(frozen=True)
class CreatePageInDb_ST:
    parent: DbParent_ST
    properties: dict


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
    parent: DbParent_ST
    archived: bool
    properties: dict
    url: str
    public_url: str


# https://developers.notion.com/reference/post-database-query
@dataclasses.dataclass(frozen=True)
class DbQueryResp_ST:
    object: str
    results: list[DbQueryRespResult_ST]
    next_cursor: str
    has_more: bool
    type: str
    page: dict


def purseRichText(purse_target: dict) -> RichText_ST:
    """
    BlockのRich textのNotionデータをパースして出力する
    BlockのRich text: https://developers.notion.com/reference/rich-text

    Args:
        purse_target (dict): Notionのデータ。辞書形式(Json)

    Returns:
        RichText_ST: パース結果
    """
    rich_text = RichText_ST(**purse_target)
    plain_text = rich_text.plain_text
    text = Text_ST(**rich_text.text)
    annotations = PageAnnotations_ST(**rich_text.annotations)

    ret = RichText_ST(plain_text=plain_text, text=text, annotations=annotations)
    return ret


def pursePageText(purse_target: dict) -> PageText_ST:
    """
    Rich text型のNotionデータをパースして出力する
    Rich text型: https://developers.notion.com/reference/page-property-values#rich-text

    Args:
        page_text_dict (dict): Notionのデータ。辞書形式(Json)

    Returns:
        PageText_ST: パース結果
    """
    page_text = PageText_ST(**purse_target)
    rich_texts = []
    for rich_text_elem in page_text.rich_text:
        rich_texts.append(purseRichText(rich_text_elem))

    ret = PageText_ST(rich_text=rich_texts, type=page_text.type, id=page_text.id)
    return ret


if __name__ == "__main__":
    import os

    database_id = "10f2085cf70a4c939b2710e883eb161a"

    # 秘密情報をロード
    load_dotenv()
    api_key = os.environ.get("NOTION_API_KEY")
    notion = Client(auth=api_key)

    response_dict = notion.databases.query(**{"database_id": database_id})
    response = DbQueryResp_ST(**response_dict)
    resp_result_dict = response.results[0]
    resp_result = DbQueryRespResult_ST(**resp_result_dict)
    print(resp_result)

    result_dict = response_dict["results"][0]
    page_parent_dict = result_dict["parent"]
    page_properties_dict = result_dict["properties"]
    page_text_dict = page_properties_dict["テキストヘッダー"]

    # page_parent = DbParent_ST(**page_parent_dict)
    # print(page_parent.database_id)
    # print(page_parent.type)

    # page_title = PageTitle_ST(**page_properties_dict["タイトルヘッダー"])
    page_text = pursePageText(page_text_dict)
    print(page_text.rich_text[0].annotations.color)
    print(page_text.id)
    print(page_text.type)
