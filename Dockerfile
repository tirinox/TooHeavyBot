FROM python:3.7
MAINTAINER Tirinox

# RUN apt-get update && apt-get -y install locales
# RUN locale-gen ru_RU.UTF-8 && locale-gen ru_RU

# RUN update-locale LANG=en_US.UTF-8 LC_MESSAGES=POSIX
# ENV LC_CTYPE="ru_RU.UTF-8"
# ENV LC_ALL="ru_RU.UTF-8"
# ENV LC_TIME="ru_RU.UTF-8"

ADD ./requirements.txt /req/
RUN pip install -r /req/requirements.txt

ADD ./src /app
WORKDIR /app

CMD [ "python", "main.py", ".config.yml" ]
