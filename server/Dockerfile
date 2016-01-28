FROM python:3.5

MAINTAINER Julio Cesar Fausto

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

ONBUILD COPY requirements.txt /usr/src/app
ONBUILD RUN pip install --no-cache -r requirements.txt

ONBUILD COPY . /usr/src/app

CMD ["twistd", "-y", "async_proxy_server.tac"]