FROM python:3.8.17-alpine

RUN apk update && apk add iputils-ping

ADD . /app

RUN pip install /app

WORKDIR /app

CMD ["python", "-m", "uvicorn", "pydom.api:app", "--host", "0.0.0.0"]