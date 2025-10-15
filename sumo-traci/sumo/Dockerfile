FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    sumo sumo-tools sumo-doc \
    net-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV SUMO_HOME=/usr/share/sumo

WORKDIR /sim
COPY . /sim