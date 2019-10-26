FROM python:3.7
MAINTAINER Tirinox

RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen ru_RU && locale-gen ru_RU.UTF-8 && update-locale

ADD ./requirements.txt /req/
RUN pip install -r /req/requirements.txt

ADD ./src /app
WORKDIR /app

CMD [ "python", "main.py", ".config.yml" ]
