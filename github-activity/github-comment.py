#!/usr/bin/env python3

import os

from rich import print
from github import Github
from dotenv import load_dotenv

# 秘密情報をロード
load_dotenv()

# Public Web Github
github_obj = Github(os.environ.get("GITHUB_ACCESS_TOKEN"), per_page=100)

repo = github_obj.get_repo("yellow-seed/slack_bolt_sample")
pr_objs = repo.get_pulls(state="all")
for pr_obj in pr_objs:
    print("#{0} Title: {1}, creater: {2}".format(pr_obj.number, pr_obj.title, pr_obj.user.login))

    comment_users = [pr_obj.user.login]
    comments = pr_obj.get_issue_comments()
    for comment in comments:
        comment_users.append(comment.user.login)
    comment_users = set(comment_users)
    print(comment_users)