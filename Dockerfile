FROM ubuntu:jammy

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ="Etc/UTC"

WORKDIR /usr/app

COPY . .

RUN apt-get update -qq && \
    apt-get install -y -qq \
        pkgconf \
        network-manager \
        libglib2.0-dev \
        libboost-python-dev \
        libboost-thread-dev \
        libbluetooth-dev \
        bluez \
        python3-pip && \
    pip3 install python-networkmanager

CMD ["python3", "/usr/app/main.py"]
