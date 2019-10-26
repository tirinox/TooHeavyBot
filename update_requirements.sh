#!/bin/sh

source venv/bin/activate

if test "$#" -ge 1; then
  pip install $1
fi

pip freeze > requirements.txt
cat requirements.txt
