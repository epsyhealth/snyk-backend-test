FROM python:3.8-slim

RUN pip install poetry==1.1.4
RUN poetry config virtualenvs.create false

COPY . /app
WORKDIR /app

RUN poetry install --no-dev

CMD gunicorn --bind 0.0.0.0:80 ProgImage.repository_service.server:app
