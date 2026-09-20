FROM python:3.12.3

ENV PYTHONUNBUFFERED=1

WORKDIR /apps/django_site

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./ ./
