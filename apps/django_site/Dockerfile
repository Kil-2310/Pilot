FROM python:3.12.3

ENV PYTHONUNBUFFERED=1

WORKDIR /django_app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./django_site ./django_site