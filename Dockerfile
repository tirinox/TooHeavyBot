FROM python:3.7
MAINTAINER Tirinox

ADD ./requirements.txt /req/
RUN pip install -r /req/requirements.txt

ADD ./src /app
WORKDIR /app

CMD [ "python", "main.py", ".config.yml" ]
