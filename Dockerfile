FROM alpine:latest
RUN apk update
RUN apk add py-pip py3-numpy py3-flask py3-scipy python3-dev
RUN pip install --upgrade pip
WORKDIR /app
COPY . /app

RUN pip install dash
CMD ["python3", "app.py"]
