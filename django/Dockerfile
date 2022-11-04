############
# BASE IMAGE
############
FROM python:3.9 as slim

# Configure Debian appropriately for non-interactive installs (see man 7 debconf)
ENV DEBIAN_FRONTEND=noninteractive

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update  && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        netcat \
        && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip then install python requirements.
COPY ./requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-compile -r requirements.txt \
    && rm -r $(pip cache dir)

ENV HOME=/home/django_app
ENV APP_HOME=/home/django_app/web
WORKDIR $APP_HOME

# create directory for the app user
RUN useradd -m app && \
    mkdir -p $APP_HOME/staticfiles

############
# MAIN IMAGE
############
FROM slim as main

# copy project
COPY . $APP_HOME

# change to the app user
USER app