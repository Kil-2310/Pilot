FROM python:3.12.3

ENV PYTHONUNBUFFERED=1


COPY ./certs/*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates


ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /apps/max_bot

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./ ./

CMD ["python", "main.py"]