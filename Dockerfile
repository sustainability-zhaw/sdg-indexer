FROM python:3.11.1-slim-bullseye

ENV DB_HOST=
# check every 30 days
ENV BATCH_INTERVAL=
ENV BATCH_SIZE=
ENV LOG_LEVEL=

COPY requirements.txt /requirements.txt
COPY src/ /app/

RUN pip install -r requirements.txt && \
    rm requirements.txt && \
    groupadd -r app && \
    useradd --no-log-init -r -g app app && \
    chmod -R 775 /app

WORKDIR /app

USER app

CMD [ "python main.py" ]
