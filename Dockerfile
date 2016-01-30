#!/usr/bin/env python
# Copyright (c) 2016, Julio Cesar Fausto.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this project.
#
FROM ubuntu:latest
MAINTAINER Julio Cesar Fausto <jcfausto@gmail.com>

RUN apt-get update -y
RUN apt-get upgrade -y

# Install pre-requisites
RUN apt-get -y install \
    libffi-dev \
    libssl-dev \
    python \
    python-dev \
    python-pip

COPY . /app
WORKDIR /app

RUN pip install -r server/requirements.txt

# Default port for proxy listenning
ENV ASYNC_PROXY_SERVER_PORT=8000

# Default port to serve statistics
ENV ASYNC_PROXY_STATS_PORT=8001

CMD twistd --nodaemon --python=server/async_proxy_server.py