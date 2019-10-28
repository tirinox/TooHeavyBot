#!/usr/bin/env bash

BOT_ID=`docker ps -aqf "name=thb_bot"`

if [[ "$1" == "build" ]]; then
    docker-compose up -d --build
elif [[ "$1" == "down" ]]; then
    docker-compose down
elif [[ "$1" == "up" ]]; then
    docker-compose up -d
elif [[ "$1" == "logs" ]]; then
    N=${1:-100}
    docker logs -f $BOT_ID --tail ${N}
elif [[ "$1" == "restart" ]]; then
    docker restart $BOT_ID
elif [[ "$1" == "pull" ]]; then
    git pull origin master
    docker-compose down
    docker-compose up -d --build
elif [[ "$1" == "inputs" ]]; then
    docker exec -it $BOT_ID python main_on_inputs.py
elif [[ "$1" == "activate" ]]; then
    source venv/bin/activate
elif [[ "$1" == "pip" ]]; then
    source venv/bin/activate

    if test "$#" -ge 2; then
      pip install $2
    fi

    pip freeze > requirements.txt
    cat requirements.txt
else
    echo "Usage: $0 <command>"
    echo "Commands are"
    echo "    build - tell docker-compose to build the projects"
    echo "    down - tell docker-compose to turn down the containers and etc."
    echo "    up - tell docker-compose to turn it up"
    echo "    restart - restarts the bot only"
    echo "    pull - git pull plus turn it up"
    echo "    logs - view last logs"
    echo "    inputs - run bot the in input mode (test mode without Telegram)"

    echo "Local commands (outside docker):"
    echo "    activate - activates the virtual enviroment"
    echo "    pip [package] - [installs a new package] and updates requirements.txt"

fi
