FROM python:3.8.3

ENV PYTHONUNBUFFERED 1
RUN mkdir /workspace
WORKDIR /workspace
ADD requirements.txt /workspace/
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
ADD . /workspace/
