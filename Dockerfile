#FROM ubuntu:20.04
FROM python:3.10-slim

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /MacMedia/app/requirements.txt

WORKDIR /MacMedia/app

#RUN apt update && apt install -y python3 && apt install -y python3-pip 
RUN pip3 install -r requirements.txt

COPY app /MacMedia/app
COPY config /MacMedia
COPY config /MacMedia/config
COPY application.py /MacMedia

# Copy in the music media library data file
COPY data/dev_music.html /MacMedia/data/dev_music.html

ENV FLASK_ENV=development
ENV APP_ENV=${APP_ENV:-Dev}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST:-0:0:0:0}
ENV DATABASE=${DATABASE}
ENV DB_PORT=${DB_PORT:-5432}

WORKDIR /MacMedia
EXPOSE 5000
CMD [ "gunicorn", "-b", "0.0.0.0:5000", "application:app"]