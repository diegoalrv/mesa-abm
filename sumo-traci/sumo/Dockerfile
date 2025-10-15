FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    sumo sumo-tools sumo-doc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /sim
COPY . /sim
