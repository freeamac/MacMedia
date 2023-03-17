#FROM ubuntu:20.04
FROM python:3.8.12-slim

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

WORKDIR /app

ENV FLASK_ENV development
ENV APP_ENV Dev

#RUN apt update && apt install -y python3 && apt install -y python3-pip 
RUN pip3 install -r requirements.txt

COPY app /app

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]