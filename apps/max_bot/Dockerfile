FROM python:3.12.3

ENV PYTHONUNBUFFERED=1

WORKDIR /apps/max_bot

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./ ./

CMD ["python", "main.py"]
