FROM python:3.6
MAINTAINER Skokov Stanislav <skokov.stanislav@yandex.ru>

COPY ./requirements.txt /
COPY ./small.mp4 /

RUN pip install -r /requirements.txt

COPY streamer.py /

CMD python3 /streamer.py
