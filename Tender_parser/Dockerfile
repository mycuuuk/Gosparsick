FROM python:3.10.9

RUN mkdir -p /home

WORKDIR /home
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY . /home

RUN pip install -r requirements.txt

EXPOSE 8000
