# docker build -t front -f Dockerfile_main .
FROM python:3.7-slim

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN \
 apt-get update && apt-get install libgtk2.0-dev -y && \
 python3 -m pip install -r requirements.txt --no-cache-dir

COPY . /app

ENTRYPOINT ["python3", "-u", "main.py"]
