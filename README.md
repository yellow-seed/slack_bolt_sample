# 前提
* Visual Studio Codeの拡張機能"Dev Containers"のインストール
* Docker Desktopのインストールと起動
* 上が済んだ状態でVisual Studio CodeのReopen in Containerを実行すると、開発環境が起動し、Visual Studio Codeもその内部のファイルを編集できる状態になる
* .env.example をコピーして　.env にファイル名を変更し(.env.exampleのファイル名変更するだけだとgitから.exampleが削除されてしまうので)、YOUR_API_KEYにSlackやOpenAIから取得したAPIキーなどの環境変数を入力する

# 開発環境の使い方
srcがカレントディレクトリにある状態で、以下のコマンドを実行すると、開発環境が起動する。
```
python3 app.py
```

# テストについて
以下コマンドを実行するとtestsフォルダ下のtestが実行される
```
pytest
```

# GitHub Actions自体の動作確認について
さしあたり https://github.com/nektos/act を使って、GitHub Actionsの動作確認をローカルでも行うことができる。

ただし事前にインストールする必要がある

インストール方法はMacとWindowsでバラバラなので注意。[こちらのページ](https://github.com/nektos/act)を参照して導入する

また、M1Macは実行時のactコマンドを最低でも以下にしないと実行に失敗する

```
act --container-architecture linux/amd64
```

初めてactを実行する場合、デフォルトで使用するイメージを選択するよう求められます。その情報は~/.actrcに保存されます。その際Medium Docker Imageを選ぶ。MicroにはPythonが入ってないので、今回のプロジェクトを動かすことができない。

ref: https://github.com/nektos/act#first-act-run

# 参考情報

### ディレクトリ構成の参考
https://zenn.dev/tk_resilie/articles/python_my_best_project
https://qiita.com/nokoxxx1212/items/da1832468cbd9a762a46

### slack_boltの実装
https://slack.dev/bolt-python/ja-jp/tutorial/getting-started

### linterなど
https://dev.classmethod.jp/articles/vscode_black_flake8/

### pytest
https://tech.isid.co.jp/entry/2023/05/02/Dev_Container%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E3%82%B9%E3%83%86%E3%83%83%E3%83%97%E3%83%90%E3%82%A4%E3%82%B9%E3%83%86%E3%83%83%E3%83%97%E3%81%A7%E4%BD%9C%E3%82%8BPython%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1

### .gitattributes について
[こちら](https://qiita.com/toromo/items/7b5703a695350473473d)を参照しました

### GitHub Actions について
https://docs.github.com/ja/actions/automating-builds-and-tests/building-and-testing-python

https://kakakakakku.hatenablog.com/entry/2023/02/02/111644