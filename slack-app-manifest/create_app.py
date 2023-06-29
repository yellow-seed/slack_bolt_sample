#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from configparser import ConfigParser

from rich import print
import requests
import json


class Manifest(object):
    def __init__(self, token):
        """
        初期化関数

        Args:
            token (str): Authentication token bearing required scopes.
                         Tokens should be passed as an HTTP Authorization header or alternatively, as a POST parameter.
        """
        self.token = token
        self.base_url = "https://slack.com/api/"
        self.manifest_config = None

    def getFileFromApp(self, app_id):
        """
        既存のSlack AppからManifestファイルを取得する
        https://api.slack.com/methods/apps.manifest.export

        Args:
            app_id (str): The ID of the app whose configuration you want to export as a manifest.
        """
        export_api = self.base_url + "apps.manifest.export"
        post_data = {"token": self.token, "app_id": app_id}
        response = requests.post(export_api, post_data)
        if self.__checkResponse(response, "getFileFromApp") is True:
            self.manifest_config = response.json()["manifest"]

    def saveFile(self, json_path):
        """
        Manifest Fileを保存する

        Args:
            json_path (str): File名.jsonをパス付きで指定する
        """
        with open(json_path, mode="w", encoding="utf-8") as json_file:
            json.dump(self.manifest_config, json_file, indent=4, ensure_ascii=False)

    def loadFile(self, json_path):
        """
        Manifest Fileをロードする

        Args:
            json_path (str): File名.jsonをパス付きで指定する
        """
        with open(json_path, mode="r", encoding="utf-8") as json_file:
            self.manifest_config = json.load(json_file)

    def createApp(self):
        """
        新しいAppを作成する。
        本メソッド実行前にgetFileFromAppまたはloadFileを実行している必要がある
        https://api.slack.com/methods/apps.manifest.create
        """
        create_api = self.base_url + "apps.manifest.create"
        post_data = {"token": self.token, "manifest": json.dumps(self.manifest_config)}
        response = requests.post(create_api, post_data)
        self.__checkResponse(response, "createApp")

    def deleteApp(self, app_id):
        """
        既存のAppを削除する
        https://api.slack.com/methods/apps.manifest.delete

        Args:
            app_id (str): The ID of the app whose configuration you want to export as a manifest.
        """
        delete_api = self.base_url + "apps.manifest.delete"
        post_data = {"token": self.token, "app_id": app_id}
        response = requests.post(delete_api, post_data)
        self.__checkResponse(response, "deleteApp")

    def changeAppConfig(self, app_id):
        """
        Applicationの設定を変更する
        本メソッド実行前にgetFileFromAppまたはloadFileを実行している必要がある
        https://api.slack.com/methods/apps.manifest.update

        Args:
            app_id (str): The ID of the app whose configuration you want to export as a manifest.
        """
        update_api = self.base_url + "apps.manifest.update"
        post_data = {"token": self.token, "app_id": app_id, "manifest": json.dumps(self.manifest_config)}
        response = requests.post(update_api, post_data)
        self.__checkResponse(response, "changeAppConfig")

    def __checkResponse(self, response, method_name=""):
        """
        This Method check the response for requests.

        Args:
            response (object): response object returned requests function.
        """
        if response.status_code == 200:
            post_result = response.json()
            if post_result["ok"] is False:
                print(method_name, "エラー!", post_result["error"], "Slackへの反映に失敗しました")
                print(post_result["errors"])
                ret = False
            else:
                print(method_name, post_result)
                ret = True
        else:
            print(method_name, response.status_code, response.reason)
            ret = False

        return ret


if __name__ == "__main__":
    # 環境変数を設定
    load_dotenv()
    # 設定値をロード
    config = ConfigParser()
    config.read("./slack-app-manifest/config.ini", encoding="utf-8")

    token = os.environ.get("SLACK_CONF_TOKEN")
    app_id = config.get("Slack", "app_id")
    file_path = config.get("Manifest", "file_path")

    manifest = Manifest(token)

    # ManifestファイルをSlack Applicationからもってきて、PCに保存する
    manifest.getFileFromApp(app_id)
    manifest.saveFile(file_path)

    # PCに保存したManifestファイルをSlack Applicationに反映する
    # manifest.loadFile(file_path)
    # manifest.changeAppConfig(app_id)

    # 新しいSlack Applicationを作成する
    # manifest.createApp()

    # 既存のSlack Applicationを削除する
    # delete_app_id = XXXXX
    # manifest.deleteApp(delete_app_id)
