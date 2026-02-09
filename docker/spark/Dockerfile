# docker/spark/Dockerfile
FROM apache/spark:3.5.1

USER root

# 1. Get the boring OS stuff out of the way
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Make Pip shiny and new
RUN pip install --upgrade pip setuptools wheel

ENV PIP_PREFER_BINARY=1

# 3. Feed the Python snake its dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# --- NEW SECTION STARTS HERE ---
# 4. Carve out a cozy home for our jobs
WORKDIR /opt/spark/jobs

# 5. Beam the code into the container
# (Assumes you're building from the project root, don't miss!)
COPY spark_jobs/ /opt/spark/jobs/

# 6. Open the doors (permissions) so Spark doesn't complain
RUN chmod -R 755 /opt/spark/jobs

# 7. Put things back where I found them (default WORKDIR)
WORKDIR /opt/spark/work-dir
# --- NEW SECTION ENDS HERE ---