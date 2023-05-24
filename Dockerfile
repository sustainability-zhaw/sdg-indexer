FROM python:3.11.1-slim-bullseye

ENV BATCH_INTERVAL=180
ENV BATCH_SIZE=100
ENV LOG_LEVEL=DEBUG

COPY requirements.txt /requirements.txt

RUN groupadd app && \
    useradd --no-log-init -m -g app app && \
    mkdir /app && \
    chmod -R 775 /app

RUN pip install -r requirements.txt && \
    rm requirements.txt

COPY src/ /app/

USER app

RUN python -c "import nltk;nltk.download('punkt');nltk.download('stopwords')"

WORKDIR /app

CMD [ "python", "main.py" ]
