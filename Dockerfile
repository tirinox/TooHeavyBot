FROM python:3.7
MAINTAINER Tirinox

ENV LANGUAGE ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
RUN locale-gen ru_RU.UTF-8 && dpkg-reconfigure locales

ADD ./requirements.txt /req/
RUN pip install -r /req/requirements.txt

ADD ./src /app
WORKDIR /app

CMD [ "python", "main.py", ".config.yml" ]
