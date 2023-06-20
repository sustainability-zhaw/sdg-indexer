FROM python:3.11.4-slim-bullseye

ENV BATCH_INTERVAL=180
ENV BATCH_SIZE=100
ENV LOG_LEVEL=DEBUG

RUN groupadd -r app && \
    useradd --no-log-init -r -m -g app app

COPY requirements.txt .
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt && \
    rm requirements.txt
    
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt stopwords

COPY src/ /app/
RUN chmod -R 775 /app

USER app

WORKDIR /app

CMD [ "python", "main.py" ]
