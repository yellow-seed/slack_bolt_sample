#!/usr/bin/env python3

from dotenv import load_dotenv
from rich import print
import dataclasses

from notion_client import Client


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


# https://developers.notion.com/reference/user#all-users (type)
# 定数であることを_Constで表現している。
# もっと良い方法があれば教えてください。
@dataclasses.dataclass(frozen=True)
class UsersType_Const:
    person: str = "person"
    bot: str = "bot"


# https://developers.notion.com/reference/user#all-users
@dataclasses.dataclass(frozen=True)
class AllUsers_ST:
    id: str
    object: str = "user"
    type: UsersType_Const = UsersType_Const.person
    name: str = None
    avatar_url: str = None


# https://developers.notion.com/reference/emoji-object
@dataclasses.dataclass(frozen=True)
class Emoji_ST:
    emoji: str = "😻"
    type: str = "emoji"


# ここまで基本要素
# ここから下はPageの要素
# Pageの要素は上の基本要素の組み合わせで成り立っている。
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


# ここからはENDPOINTSの要素
# https://developers.notion.com/reference/post-page
@dataclasses.dataclass(frozen=True)
class CreatePageInDb_ST:
    parent: DbParent_ST
    properties: dict


# https://developers.notion.com/reference/post-database-query
# RESPONSE["results"]の要素
@dataclasses.dataclass(frozen=True)
class DbQueryResResult_ST:
    object: str
    id: str
    created_time: str
    last_edited_time: str
    created_by: AllUsers_ST
    last_edited_by: AllUsers_ST
    cover: str
    icon: Emoji_ST
    parent: DbParent_ST
    archived: bool
    properties: dict
    url: str
    public_url: str


# https://developers.notion.com/reference/post-database-query
# RESPONSEの要素
@dataclasses.dataclass(frozen=True)
class DbQueryRes_ST:
    object: str
    results: list[DbQueryResResult_ST]
    next_cursor: str
    has_more: bool
    type: str
    page: dict


# ここからパーサーの関数を定義
def purseRichText(purse_target: dict) -> RichText_ST:
    """
    BlockのRich textのNotionデータをパースして出力する
    参照: https://developers.notion.com/reference/rich-text

    Args:
        purse_target (dict): Notionのデータ。辞書形式(Json)

    Returns:
        RichText_ST: パース結果
    """
    rich_text = RichText_ST(**purse_target)  # 辞書からクラスに戻す時はアンパックを使う: https://qiita.com/ttyszk/items/01934dc42cbd4f6665d2
    ret = RichText_ST(
        plain_text=rich_text.plain_text,
        text=Text_ST(**rich_text.text),
        annotations=PageAnnotations_ST(**rich_text.annotations),
        href=rich_text.href,
        type=rich_text.type,
    )
    return ret


def pursePageText(purse_target: dict) -> PageText_ST:
    """
    Rich text型のNotionデータをパースして出力する
    参照: https://developers.notion.com/reference/page-property-values#rich-text

    Args:
        page_text_dict (dict): Notionのデータ。辞書形式(JSON)

    Returns:
        PageText_ST: パース結果
    """
    page_text = PageText_ST(**purse_target)
    rich_texts = []
    for rich_text_elem in page_text.rich_text:
        rich_texts.append(purseRichText(rich_text_elem))

    ret = PageText_ST(
        rich_text=rich_texts,
        type=page_text.type,
        id=page_text.id,
    )
    return ret


def purseDbParent(purse_target: dict) -> DbParent_ST:
    """
    Database parent型のNotionデータをパースして出力する
    参照: https://developers.notion.com/reference/parent-object#database-parent

    Args:
        purse_target (dict): Notionのデータ。辞書形式(JSON)

    Returns:
        PageParent_ST: パース結果
    """
    page_parent = DbParent_ST(**purse_target)
    ret = DbParent_ST(database_id=page_parent.database_id, type=page_parent.type)
    return ret


def pursePageParent(purse_target: dict) -> PageParent_ST:
    """
    Page parent型のNotionデータをパースして出力する
    参照: https://developers.notion.com/reference/parent-object#page-parent

    Args:
        purse_target (dict): Notionのデータ。辞書形式(JSON)

    Returns:
        PageParent_ST: パース結果
    """
    page_parent = PageParent_ST(**purse_target)
    ret = PageParent_ST(page_id=page_parent.page_id, type=page_parent.type)
    return ret


def purseDbQueryRes(purse_target: dict) -> DbQueryRes_ST:
    """
    database queryのRESPONSEのNotionデータをパースして出力する
    参照: https://developers.notion.com/reference/post-database-query

    Args:
        purse_target (dict): Notionのデータ。辞書形式(JSON)

    Returns:
        DbQueryRes_ST: パース結果
    """
    res_result = DbQueryRes_ST(**purse_target)
    results_list = []
    for result in res_result.results:
        results_list.append(purseDbQueryRespResult(result))

    ret = DbQueryRes_ST(
        object=res_result.object,
        results=results_list,
        next_cursor=res_result.next_cursor,
        has_more=res_result.has_more,
        type=res_result.type,
        page=res_result.page,
    )
    return ret


def purseDbQueryRespResult(purse_target: dict) -> DbQueryResResult_ST:
    """
    database queryのRESPONSE["results"]のNotionデータをパースして出力する
    参照: https://developers.notion.com/reference/post-database-query

    Args:
        purse_target (dict): Notionのデータ。辞書形式(JSON)

    Returns:
        DbQueryResResult_ST: パース結果
    """
    res_result = DbQueryResResult_ST(**purse_target)
    if res_result.icon is not None:
        icon = Emoji_ST(**res_result.icon)
    else:
        icon = None

    ret = DbQueryResResult_ST(
        object=res_result.object,
        id=res_result.id,
        created_time=res_result.created_time,
        last_edited_time=res_result.last_edited_time,
        created_by=AllUsers_ST(**res_result.created_by),
        last_edited_by=AllUsers_ST(**res_result.last_edited_by),
        cover=res_result.cover,
        icon=icon,
        parent=DbParent_ST(**res_result.parent),
        archived=res_result.archived,
        properties=res_result.properties,
        url=res_result.url,
        public_url=res_result.public_url,
    )
    return ret


if __name__ == "__main__":
    import os

    database_id = "10f2085cf70a4c939b2710e883eb161a"

    # 秘密情報をロード
    load_dotenv()
    api_key = os.environ.get("NOTION_API_KEY")
    notion = Client(auth=api_key)

    response_dict = notion.databases.query(**{"database_id": database_id})
    db_query_res = purseDbQueryRes(response_dict)
    page_properties_dict = db_query_res.results[0].properties
    page_text_dict = page_properties_dict["テキストヘッダー"]

    # print(db_query_res.results[0].parent)
    # print(db_query_res.results[0].id)
    # print(db_query_res.results[0].created_by)
    print(db_query_res.results[0].properties)

    # page_parent = DbParent_ST(**page_parent_dict)
    # print(page_parent.database_id)
    # print(page_parent.type)

    page_title = PageTitle_ST(**page_properties_dict["タイトルヘッダー"])
    page_text = pursePageText(page_text_dict)
    print(page_text.rich_text[0].annotations.color)
    print(page_text.id)
    print(page_text.type)
    print(page_text.rich_text[0].href)
    print(page_text.rich_text[0].type)
