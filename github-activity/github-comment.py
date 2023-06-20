#!/usr/bin/env python3

import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../notion_db_sample")

from rich import print
from dotenv import load_dotenv
from configparser import ConfigParser

from github import Github
from time import sleep

from pynotion import DbContents


def countComment(comment_users, login_name):
    """
    Comment数をCountする。

    Args:
        comment_users (list): Count対象のユーザ名が記されているlist
        login_name (str): listに含まれているCountしたいユーザ名

    Returns:
        int: number of count
    """
    ret_count = comment_users.count(login_name)
    if ret_count == 0:
        ret_count = None

    return ret_count


def isPullReqUpdated(notion_rows: dict, github_target: dict) -> bool:
    """
        GithubのあるPRのコメント数が更新されているかチェックする

    Args:
        notion_rows (dict): Notion側の情報
        github_target (dict): Github側の情報

    Returns:
        bool: True 更新されている/新規のPRである。 False 更新されていない
    """
    result = False
    pr_num = github_target["No."]
    for notion_row in notion_rows:
        if pr_num == notion_row["No."]:
            break
    else:
        # No.該当なし。つまり新しいPRである。
        return True

    for key, notion_value in notion_row.items():
        if type(notion_value) == list:
            if github_target[key] != notion_value[0]:
                result = True
                break
        else:  # type(notion_value) != list
            if github_target[key] != notion_value:
                result = True
                break
    else:
        result = False

    return result


if __name__ == "__main__":
    # 情報をロード
    load_dotenv()
    config = ConfigParser()
    config.read("/workspaces/slack_bolt_sample/github-activity/config.ini", encoding="utf-8")
    table_id = config.get("Database", "gh_comment_table_id")
    repository = config.get("Github", "repository")
    notion_api_key = os.environ.get("NOTION_API_KEY")
    github_access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
    ito_login_name = config.get("Github", "ito_login_name")
    iwama_login_name = config.get("Github", "iwama_login_name")
    uemura_login_name = config.get("Github", "uemura_login_name")
    tanaka_login_name = config.get("Github", "tanaka_login_name")
    nakauchi_login_name = config.get("Github", "nakauchi_login_name")
    nakagawa_login_name = config.get("Github", "nakagawa_login_name")
    baba_login_name = config.get("Github", "baba_login_name")

    # Notion DBオブジェクト作成
    db_contents = DbContents(notion_api_key)
    # データを取得
    notion_rows = db_contents.pull(table_id)

    # ここからGithubのAPIを使用したサンプル
    # Public Web Github
    github_obj = Github(github_access_token, per_page=100)

    repo = github_obj.get_repo(repository)
    pr_objs = repo.get_pulls(state="all")

    for pr_obj in pr_objs:
        print("#{0} Title: {1}, 作成者: {2}".format(pr_obj.number, pr_obj.title, pr_obj.user.login))

        create_date = "{0}".format(pr_obj.created_at).split(" ")[0]  # 例えば、2023-05-19 14:59:40の日付部分2023-05-19を抽出
        pr_status = None

        if pr_obj.merged_at != None:
            pr_status = "Merged"
        else:
            if pr_obj.state == "closed":
                pr_status = "Closed"
            else:
                pr_status = "Open"

        # コメント数を集計する
        comment_users = [pr_obj.user.login]
        # 通常コメント
        comments = pr_obj.get_issue_comments()
        for comment in comments:
            comment_users.append(comment.user.login)
        # Reviewコメント
        comments = pr_obj.get_review_comments()
        for comment in comments:
            comment_users.append(comment.user.login)

        pr_dict = {
            "No.": pr_obj.number,
            "タイトル": pr_obj.title,
            "作成者": pr_obj.user.login,
            tanaka_login_name: countComment(comment_users, tanaka_login_name),
            baba_login_name: countComment(comment_users, baba_login_name),
            ito_login_name: countComment(comment_users, ito_login_name),
            nakagawa_login_name: countComment(comment_users, nakagawa_login_name),
            uemura_login_name: countComment(comment_users, uemura_login_name),
            nakauchi_login_name: countComment(comment_users, nakauchi_login_name),
            iwama_login_name: countComment(comment_users, iwama_login_name),
            "作成日": create_date,
            "ステータス": pr_status,
            "URL": pr_obj.html_url,
        }
        if isPullReqUpdated(notion_rows, pr_dict) == True:
            sleep(0.5)
            db_contents.delete("No.", pr_obj.number)

            # データを追加
            sleep(0.5)
            db_contents.append(pr_dict)
