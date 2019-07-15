FROM python:3-alpine

ADD . /app
WORKDIR /app

RUN apk add --no-cache openssl && \
    apk add --no-cache --virtual .build gcc musl-dev libffi-dev openssl-dev make && \
    pip install -r requirements.txt && \
    apk del .build

CMD ["python", "main.py"]