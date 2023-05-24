FROM python:3.11.1-slim-bullseye

ENV BATCH_INTERVAL=180
ENV BATCH_SIZE=100
ENV LOG_LEVEL=DEBUG

RUN groupadd app && \
    useradd --no-log-init -m -g app app

COPY requirements.txt /requirements.txt
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY src/ /app/
RUN chmod -R 775 /app

USER app
RUN python -c "import nltk;nltk.download('punkt');nltk.download('stopwords')"

WORKDIR /app

CMD [ "python", "main.py" ]
