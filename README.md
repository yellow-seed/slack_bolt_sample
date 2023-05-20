# 前提
* Visual Studio Codeの拡張機能"Dev Containers"のインストール
* Docker Desktopのインストールと起動
* 上が済んだ状態でVisual Studio CodeのReopen in Containerを実行すると、開発環境が起動し、Visual Studio Codeもその内部のファイルを編集できる状態になる
* .env.example を　.env にファイル名を変更し、SlackやOpenAIから取得したAPIキーなどの環境変数を入力する

# 開発環境の使い方
srcがカレントディレクトリにある状態で、以下のコマンドを実行すると、開発環境が起動する。
```
python3 app.py
```

### ディレクトリ構成の参考
https://zenn.dev/tk_resilie/articles/python_my_best_project
https://qiita.com/nokoxxx1212/items/da1832468cbd9a762a46

### slack_boltの実装
https://slack.dev/bolt-python/ja-jp/tutorial/getting-started

### linterなど
https://dev.classmethod.jp/articles/vscode_black_flake8/

### .gitattributes について
[こちら](https://qiita.com/toromo/items/7b5703a695350473473d)を参照しました