FROM python:3.9.5-slim-buster

RUN apt update \
  && apt install netcat -y \
  && apt clean

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

ENV FLASK_ENV production
ENV APP_SETTINGS src.config.ProductionConfig

COPY requirements/common.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser --disabled-password user
USER user

CMD gunicorn --bind 0.0.0.0:$PORT manage:app
