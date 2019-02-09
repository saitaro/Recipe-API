FROM python:3.7-alpine
LABEL maintainer="Victor B" 

# RUN pip3 install pipenv

# COPY ./Pipfile /Pipfile
# COPY ./Pipfile.lock /Pipfile.lock 

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
# RUN pipenv install

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user