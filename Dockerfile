FROM mcr.microsoft.com/devcontainers/python:0-3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
# MOB Dockerfile production用も作成する