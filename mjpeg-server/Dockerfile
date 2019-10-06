FROM python:3.6
MAINTAINER Skokov Stanislav <skokov.stanislav@yandex.ru>

COPY ./requirements.txt /src/
RUN pip install -r /src/requirements.txt

COPY ./no-image.png /src/
COPY ./server.py /src/
WORKDIR /src/

CMD gunicorn --timeout=300 --log-level=debug -w=1 --bind 0.0.0.0:5000 --threads 20 --keep-alive=9999999999 server:app
