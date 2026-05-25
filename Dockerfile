# pull official base image
# Using Python 3.8 for ARM64 (Apple Silicon) compatibility
FROM python:3.10

# set work directory
WORKDIR /usr/src/ludo

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV SIU_URL $SIU_URL

# install system dependencies for psycopg2 and opencv (libGL is needed by cv2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        libgl1 \
        libglib2.0-0 \
        curl \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip
RUN pip install "setuptools<81" wheel
RUN pip install --upgrade Pillow
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# download face detection/recognition ONNX models from OpenCV Zoo
# (baked into image for Heroku; in local dev the volume mount shadows these,
# so entrypoint.sh re-downloads on start if missing)
RUN mkdir -p /usr/src/ludo/backend/services/models
# RUN mkdir -p /usr/src/ludo/backend/services/models \
    # && curl -fSL -o /usr/src/ludo/backend/services/models/face_detection_yunet_2023mar.onnx \
    #     https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx \
    # && curl -fSL -o /usr/src/ludo/backend/services/models/face_recognition_sface_2021dec.onnx \
    #     https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx

# collect static files
RUN python manage.py collectstatic --noinput

# copy entrypoint and give execute permissions
COPY entrypoint.sh .
RUN chmod +x /usr/src/ludo/entrypoint.sh

# run entrypoint.sh (waits for db and runs migrations)
ENTRYPOINT ["/usr/src/ludo/entrypoint.sh"]

CMD gunicorn ludo.wsgi:application --bind 0.0.0.0:$PORT

