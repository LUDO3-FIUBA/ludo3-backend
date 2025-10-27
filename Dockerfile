# pull official base image
# Using Python 3.8 for ARM64 (Apple Silicon) compatibility
FROM python:3.8

# set work directory
WORKDIR /usr/src/ludo

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV SIU_URL $SIU_URL

# install system dependencies for psycopg2 and face_recognition
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libpq-dev \
        libopenblas-dev \
        liblapack-dev \
        libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
RUN pip install --upgrade Pillow
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# collect static files
RUN python manage.py collectstatic --noinput

CMD gunicorn ludo.wsgi:application --bind 0.0.0.0:$PORT

