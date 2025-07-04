FROM python:3.13.4-slim-bookworm

ENV BATCH_INTERVAL=180
ENV BATCH_SIZE=100
ENV LOG_LEVEL=DEBUG

RUN groupadd -r app && \
    useradd --no-log-init -r -m -g app app


COPY requirements.txt .

# Use this block with caution and only if the transformer models are installed.
#
# It will install cmake and other dependencies and add about 400MB to the image.
# RUN apt update && \
    # apt install -y --no-install-recommends \
        # cmake \
        # && \
    # rm -rf /var/lib/apt/lists/* && \
    # apt clean

RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt && \
    # rm requirements.txt && \
    # Spacy base models
    python -m spacy download en_core_web_sm && \
    python -m spacy download fr_core_news_sm && \
    python -m spacy download de_core_news_sm && \
    python -m spacy download it_core_news_sm 
    #
    # Spacy transformer models (500MB each!)
    # Install either base or transformer models!
    #
    # Important: the french model requires cmake to install :&
    #
    # python -m spacy download en_core_web_trf && \
    # python -m spacy download fr_dep_news_trf && \
    # python -m spacy download de_dep_news_trf && \
    # python -m spacy download it_core_news_lg

COPY src/ /app/
RUN chmod -R 775 /app

USER app

WORKDIR /app

CMD [ "python", "main.py" ]
