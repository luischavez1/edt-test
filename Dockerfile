
FROM python:3.11.6-slim as builder

WORKDIR /code

RUN apt-get update \
  && apt-get clean \
  && apt-get -y install libpq-dev curl

COPY . ./

RUN pip install -r requirements.txt

# install DBMATE
RUN curl -fsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64
RUN chmod +x /usr/local/bin/dbmate

CMD ["uvicorn", "app.main:app","--reload", "--host", "0.0.0.0", "--port", "8000"]
