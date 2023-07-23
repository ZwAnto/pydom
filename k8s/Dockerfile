FROM python:3.8.13-slim-buster

RUN apt-get update && apt-get install -y iputils-ping

ADD . /app

RUN pip install /app

WORKDIR /app

CMD ["python", "-m", "uvicorn", "pydom.api:app", "--host", "0.0.0.0"]