# https://cloud.google.com/run/docs/quickstarts/build-and-deploy
#
# export PROJECT_ID=`gcloud config get-value project`
# export SLACK_APP_TOKEN=
# export SLACK_BOT_TOKEN=
# gcloud builds submit --tag gcr.io/$PROJECT_ID/helloworld
# gcloud run deploy helloworld --image gcr.io/$PROJECT_ID/helloworld --platform managed --update-env-vars SLACK_SIGNING_SECRET=$SLACK_APP_TOKEN,SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN
#

# ----------------------------------------------
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8.5-slim-buster

# ステートメントやログメッセージをKnativeのログに即座に表示できるようにする
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -U pip && pip install -r requirements.txt

# Run the web service on container startup.
ENTRYPOINT gunicorn --bind :$PORT --workers 1 --threads 2 --timeout 0 main:flask_app
# ↓ローカルで確認する場合はコメントアウトを外す
# ENTRYPOINT gunicorn --bind :3000 --workers 1 --threads 2 --timeout 0 main:flask_app