#!/bin/sh

if [ "$DATABASE" = "postgres" ] && [ -n "$SQL_HOST" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

MODELS_DIR=/usr/src/ludo/backend/services/models
YUNET=$MODELS_DIR/face_detection_yunet_2023mar.onnx
SFACE=$MODELS_DIR/face_recognition_sface_2021dec.onnx
mkdir -p "$MODELS_DIR"
if [ ! -s "$YUNET" ]; then
    echo "Downloading YuNet face detector..."
    curl -fSL -o "$YUNET" https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
fi
if [ ! -s "$SFACE" ]; then
    echo "Downloading SFace face recognizer..."
    curl -fSL -o "$SFACE" https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx
fi

python manage.py migrate

exec "$@"
