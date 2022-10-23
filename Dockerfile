FROM python:3.10.4-alpine
ENV PIP_NO_CACHE_DIR 1
COPY requirements.txt /userbot/requirements.txt
WORKDIR /userbot
RUN pip install -Ur requirements.txt
COPY . .
CMD python -m userbot
