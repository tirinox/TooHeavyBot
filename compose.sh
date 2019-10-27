#!/usr/bin/env bash

if [[ "$1" == "build" ]]; then
    docker-compose up -d --build
elif [[ "$1" == "down" ]]; then
    docker-compose down
elif [[ "$1" == "up" ]]; then
    docker-compose up -d
elif [[ "$1" == "logs" ]]; then
    N=${1:-100}
    docker logs -f `docker ps -aqf "name=thb_bot"` --tail ${N}
elif [[ "$1" == "restart" ]]; then
    docker restart `docker ps -aqf "name=thb_bot"`
elif [[ "$1" == "pull" ]]; then
    git pull origin master
    docker-compose down
    docker-compose up -d --build
else
    echo "Usage: $0 [up|build|down|pull|logs]"
fi
