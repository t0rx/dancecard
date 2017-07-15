FROM python:3

RUN pip install paho-mqtt pyyaml

RUN mkdir -p /opt/dancecard
WORKDIR /opt/dancecard

COPY *.py ./

ENTRYPOINT [ "python3", "./dancecard.py" ]
