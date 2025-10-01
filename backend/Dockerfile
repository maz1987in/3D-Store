# dockerfile for flask app
# Language: dockerfile
# Path: Dockerfile

#FROM python:3.6-alpine
ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim-buster as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Set environment variables for timezone
ENV TZ=Asia/Muscat

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
    
# Install dependencies for Postgres
#RUN apt-get update && \
#    apt-get install -y libpq-dev gcc \
#    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
    apt-get install -y \
#    ca-certificates \
    wget \
    openssl \
    tzdata \
    libmagic1 && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# Download the public SSL certificate
# This command connects to the specified domain, gets the certificate and outputs it into a file
#RUN openssl s_client -showcerts -connect smartpaytrns.bankmuscat.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM > smartpaytrns.bankmuscat.com.pem
# Add the certificate to the trusted CA store
#RUN cp smartpaytrns.bankmuscat.com.pem /usr/local/share/ca-certificates/smartpaytrns.bankmuscat.com.crt \
#    && update-ca-certificates
    
WORKDIR /app

ARG APP_ENV=development
ENV APP_ENV=${APP_ENV}

COPY env_production .env

#RUN if [ "$ENV" = "production" ] ; then COPY env_development .env ; else COPY env_prod .env ; fi
COPY requirements requirements
COPY requirements.txt requirements.txt

# Set up a virtual environment
RUN python -m venv /venv

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements,target=requirements \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --upgrade pip
RUN /venv/bin/pip install -r requirements.txt gunicorn
#    /venv/bin/pip install gunicorn 



# Copy the source code into the container.
#COPY . .

#RUN pip3 install gunicorn


#COPY app app
#COPY alembic alembic
COPY boot.sh ./
RUN chown -R appuser:appuser .env requirements requirements.txt 
RUN chmod +x boot.sh 
RUN mkdir -p logs && chown -R appuser:appuser logs
#RUN chown -R appuser:appuser logs boot.sh

# Switch to the non-privileged user to run the application.
USER appuser
COPY *.py alembic.ini ./ 
COPY app app
COPY alembic alembic

# Set the environment variables
ENV FLASK_APP=run.py \
    LOG_TYPE=stream \
    FLASK_RUN_HOST=0.0.0.0 \
    ENV=${APP_ENV} \
    DB_TYPE=mysql \
    DB_HOST=db \
    DB_USERNAME=root \
    DB_PASSWORD=password \
    DB_DATABASE_NAME=database \
    CACHE_TYPE=SimpleCache \
    CACHE_REDIS_HOST=redis \
    CACHE_REDIS_PORT=6379 \
    CACHE_REDIS_DB=0 \
    CACHE_REDIS_PASSWORD= \
    SCHEDULER_ENABLED=True \
    SCHEDULER_MODE=memory \
    SCHEDULER_REDIS_HOST=redis \
    SCHEDULER_REDIS_PORT=6379 \
    SCHEDULER_REDIS_DB=1 \
    SCHEDULER_REDIS_PASSWORD=

#RUN chown -R store3d:store3d ./
#USER store3d

EXPOSE 5000
# Use the virtual environment
ENV PATH="/venv/bin:$PATH"

# Run the application
# Run gunicorn when the container launches
#CMD ["gunicorn", "-b", ":5000", "run:app"]

ENTRYPOINT ["./boot.sh"]
