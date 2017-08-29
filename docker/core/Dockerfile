FROM python:3

RUN pip install paho-mqtt pyyaml

RUN mkdir -p /opt/dancecard /etc/dancecard
VOLUME /etc/dancecard

WORKDIR /opt/dancecard
COPY python/*.py python/

ENTRYPOINT [ "python3", "python/dancecard.py" ]
