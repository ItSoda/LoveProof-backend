FROM python:3.10-alpine

SHELL ["/bin/ash", "-c"]

EXPOSE 8000

RUN apk cache clean && apk update
RUN apk add --no-cache bash curl && \
    apk add --no-cache rsync openssh-client sshpass && \
    apk add --no-cache build-base mariadb-dev && \
    apk add --no-cache docker-compose && \
    apk add --no-cache postgresql-client 

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

RUN pip install --upgrade pip

RUN adduser -D loveproof && chmod 777 /opt /run

WORKDIR /loveproof

RUN mkdir /loveproof/static && mkdir /loveproof/media && chown -R loveproof:loveproof /loveproof && chmod 777 /loveproof

COPY --chown=loveproof:loveproof . .

COPY pyproject.toml poetry.lock /loveproof/

RUN curl -L https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    | tar -C /usr/local/bin -xzvf - \
    && rm -f dockerize-linux-amd64-v0.6.1.tar.gz

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi
