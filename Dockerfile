FROM python:3.11.1-slim-bullseye

ENV BATCH_INTERVAL=180
ENV BATCH_SIZE=100
ENV LOG_LEVEL=DEBUG

COPY requirements.txt /requirements.txt

RUN mkdir -p /app && \
    pip install -r requirements.txt && \
    rm requirements.txt && \
    python -c "import nltk;nltk.download('punkt');nltk.download('stopwords')" && \
    groupadd -r app && \
    useradd --no-log-init -r -g app app && \
    chmod -R 775 /app

COPY src/ /app/

WORKDIR /app

USER app

CMD [ "python", "main.py" ]
