import io
import os

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from backend.api_exceptions import FaceRegistrationPendingError, InvalidImageError
from backend.utils import decode_image

_MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
_DETECTOR_PATH = os.path.join(_MODELS_DIR, "face_detection_yunet_2023mar.onnx")
_RECOGNIZER_PATH = os.path.join(_MODELS_DIR, "face_recognition_sface_2021dec.onnx")

# OpenCV-recommended threshold for SFace with cosine distance is 0.363; we use a more
# permissive value to tolerate lighting/angle variation between registration and verification.
_COSINE_MATCH_THRESHOLD = 0.30

_detector = None
_recognizer = None


def _get_detector(width, height):
    global _detector
    if _detector is None:
        _detector = cv2.FaceDetectorYN.create(
            model=_DETECTOR_PATH,
            config="",
            input_size=(width, height),
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=50,
        )
    else:
        _detector.setInputSize((width, height))
    return _detector


def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        _recognizer = cv2.FaceRecognizerSF.create(
            model=_RECOGNIZER_PATH,
            config="",
        )
    return _recognizer


class ImageValidatorService:
    def __init__(self, b64_string):
        self.b64_string = b64_string

    def validate_identity(self, user):
        stored = getattr(user, "face_encodings", None) or []
        if not stored:
            raise FaceRegistrationPendingError()

        self.validate_image()

        stored_feature = np.array(stored, dtype=np.float32).reshape(1, -1)
        new_feature = np.array(self.face_encodings[0], dtype=np.float32).reshape(1, -1)
        score = _get_recognizer().match(new_feature, stored_feature, cv2.FaceRecognizerSF_FR_COSINE)
        return bool(score >= _COSINE_MATCH_THRESHOLD)

    def validate_image(self):
        self._validate_encoding()
        self._detect_face()
        return self.face_encodings[0], self.image

    def _validate_encoding(self):
        try:
            raw_bytes = decode_image(self.b64_string)
            self.image = Image.open(io.BytesIO(raw_bytes))
            self.image.load()
        except (UnidentifiedImageError, ValueError, OSError):
            raise InvalidImageError(detail="Invalid base64 string, not an image")

        array = np.frombuffer(raw_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if bgr is None:
            raise InvalidImageError(detail="Invalid base64 string, not an image")
        self._bgr_image = bgr

    def _detect_face(self):
        height, width = self._bgr_image.shape[:2]
        detector = _get_detector(width, height)
        _, faces = detector.detect(self._bgr_image)
        if faces is None or len(faces) == 0:
            raise InvalidImageError(detail="Invalid image, could not detect face")

        # Pick the highest-confidence face (last column is score).
        best = max(faces, key=lambda f: f[-1])
        aligned = _get_recognizer().alignCrop(self._bgr_image, best)
        feature = _get_recognizer().feature(aligned)
        # feature is shape (1, 128); store as flat python list of floats.
        self.face_encodings = [feature.flatten().astype(float).tolist()]
