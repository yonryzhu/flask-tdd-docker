FROM python:3.9.5-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update \
    && apt install netcat -y \
    && apt clean

COPY ./requirements/base.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
