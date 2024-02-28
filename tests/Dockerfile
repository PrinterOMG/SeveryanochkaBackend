FROM python:3.11
LABEL authors="printeromg"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app/

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["pytest", "-v"]