FROM python:3.9-slim-buster

ARG PYGOBJECT_WITHOUT_PYCAIRO=1

WORKDIR /usr/app

RUN apt-get update -qq

RUN apt-get install --no-install-recommends -y \
    build-essential \
    cmake \
    autoconf \
    dbus \
    libdbus-1-dev \
    libglib2.0-dev \
    libgirepository1.0-dev

COPY requirements.txt requirements.txt

RUN pip3 install --no-build-isolation -r requirements.txt

RUN apt-get remove build-essential cmake autoconf -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python3", "/usr/app/main.py"]
