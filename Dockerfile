FROM python:3.8.13-slim-buster

ADD . /app

RUN pip install /app

CMD ["python", "-m", "uvicorn", "pydom.main:app", "--host", "0.0.0.0"]