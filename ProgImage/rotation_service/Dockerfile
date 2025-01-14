FROM python:3.14.0a3-alpine3.21

RUN pip install poetry==1.1.4
RUN poetry config virtualenvs.create false

COPY . /app
WORKDIR /app

RUN poetry install --no-dev

CMD gunicorn --bind 0.0.0.0:80 ProgImage.rotation_service.server:app
