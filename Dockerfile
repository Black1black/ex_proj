FROM python:3.12

RUN mkdir /example_project

WORKDIR /example_project

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .


