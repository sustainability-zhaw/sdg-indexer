FROM python:3.12.1-slim-bookworm

ENV BATCH_INTERVAL=180
ENV BATCH_SIZE=100
ENV LOG_LEVEL=DEBUG

RUN groupadd -r app && \
    useradd --no-log-init -r -m -g app app

COPY requirements.txt .
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# NLTK models    
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt stopwords

# Spacy models
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download fr_core_news_sm && \
    python -m spacy download de_core_news_sm && \
    python -m spacy download it_core_news_sm && \
    python -m spacy download en_core_web_trf && \
    python -m spacy download fr_dep_news_trf && \
    python -m spacy download de_dep_news_trf && \
    python -m spacy download it_core_news_lg

COPY src/ /app/
RUN chmod -R 775 /app

USER app

WORKDIR /app

CMD [ "python", "main.py" ]
