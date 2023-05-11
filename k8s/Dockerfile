FROM python:3.8.13-slim-buster

RUN apt update && apt install -y iputils-ping

ADD . /app

RUN pip install /app

WORKDIR /app

CMD ["python", "-m", "uvicorn", "pydom.api:app", "--host", "0.0.0.0"]