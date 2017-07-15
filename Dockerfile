FROM python:3

RUN mkdir -p /opt/dancecard
WORKDIR /opt/dancecard

COPY *.py ./

ENTRYPOINT [ "python3", "./dancecard.py" ]
