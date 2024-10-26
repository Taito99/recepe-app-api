FROM python:3.12-alpine3.20
LABEL maintainer="amadeuszbujalskidev.com"

ENV PYTHONUNBUFFERED="1"

# Kopiowanie wymagań
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Kopiowanie folderu aplikacji
COPY ./app /app

# Ustawienie folderu roboczego na główny katalog projektu
WORKDIR /app

# Ustawienie PYTHONPATH, aby aplikacje były widoczne
ENV PYTHONPATH="/app"

EXPOSE 8000

ARG DEV=false

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; \
      then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# Ustawienie ścieżki do środowiska Pythona
ENV PATH="/py/bin:$PATH"

# Ustawienie użytkownika na django-user
USER django-user
