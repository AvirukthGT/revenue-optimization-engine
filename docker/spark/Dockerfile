# docker/spark/Dockerfile
FROM apache/spark:3.5.1

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip setuptools wheel


ENV PIP_PREFER_BINARY=1


COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt