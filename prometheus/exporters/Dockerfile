FROM ubuntu:18.04

# ------------------ Required packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y \
    curl \
    wget \
    python3-pip \
    nano \
    zip \
    git \
    net-tools \
    jq \
    unzip \
    iputils-ping \
    adduser


RUN pip3 install --upgrade pip 

RUN pip3 install --upgrade \
    pandas \
    prometheus-client \
    google-cloud-bigquery \
    boto3 \
    pyarrow \
    yandex \
    yandexcloud



