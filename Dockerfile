FROM python:3.9.5-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements/base.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD python manage.py run -h 0.0.0.0
