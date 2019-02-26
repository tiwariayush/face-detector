FROM python:3.6.5

ADD requirements.txt /api/requirements.txt

WORKDIR /api

RUN pip install -r requirements.txt
ENV PYTHONPATH /api
