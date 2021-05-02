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

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user