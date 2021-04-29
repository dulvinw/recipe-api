FROM python:3.7-alpine
MAINTAINER Dulvin Witharane

ENV PYTHONUNBUFFERED 1

RUN apk update --no-cache \
    && apk add --virtual build-deps gcc musl-dev libc-dev postgresql-dev \
    && apk add postgresql-client \
    && apk add jpeg-dev zlib-dev libjpeg

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN apk del build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user