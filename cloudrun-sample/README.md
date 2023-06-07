# ローカルで立ち上げる場合
## 前準備

### ngrok
ngrokでサーバーを立ち上げて `https://xxxx-xxxx-xxx-xxx-xxx.ngrok-free.app -> http://localhost:3000` となるようにする

```
ngrok http 3000
```

↓ngrokで生成されたURLをSlackアプリのevent-subscriptionsに登録する必要がある
https://api.slack.com/apps/A053QS5RJ1G/event-subscriptions?

※このときチャレンジ認証が行われる。下記のコードのように一回challengeを返してあげないと登録できない
```
    if 'challenge' in payload:
        # これはチャレンジリクエストです。アプリを確認するためにチャレンジ値で応答してください。
        # ref: https://qiita.com/masa_masa_ra/items/618779e698921cb53cec
        return payload['challenge']
```


## ローカルで立ち上げる場合

source .venv/bin/activate.fish
python main.py

## dockerで立ち上げる場合
docker build -t my_app .
docker run -p 3000:3000 --env-file .env  my_app


## CloudRun
export SLACK_APP_TOKEN=xxxxxxxxxxxx
export SLACK_BOT_TOKEN=xxxxxxxxxxxx
export SLACK_SIGNING_SECRET=xxxxxxxxxxxx
gcloud builds submit --tag gcr.io/$PROJECT_ID/helloworld
gcloud run deploy helloworld --image gcr.io/$PROJECT_ID/helloworld --platform managed --update-env-vars SLACK_SIGNING_SECRET=$SLACK_APP_TOKEN,SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN,SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET

## 設定
https://{ngrokやcloudrunのエンドポイント}/slack/events