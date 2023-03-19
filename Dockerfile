#FROM ubuntu:20.04
FROM python:3.8.12-slim

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /MacMedia/app/requirements.txt

WORKDIR /MacMedia/app

#RUN apt update && apt install -y python3 && apt install -y python3-pip 
RUN pip3 install -r requirements.txt

COPY app /MacMedia/app
COPY config /MacMedia
COPY config /MacMedia/config
COPY application.py /MacMedia

ENV FLASK_ENV development
ENV APP_ENV Dev

WORKDIR /MacMedia
EXPOSE 5000
CMD [ "gunicorn", "-b", "0.0.0.0:5000", "application:app"]