FROM ubuntu:22.04

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
	python3 \
	python3-pip \
	ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY script/requirements.txt ./requirements.txt

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY script/http_status_checker.py ./http_status_checker.py

CMD ["python3", "http_status_checker.py"]
