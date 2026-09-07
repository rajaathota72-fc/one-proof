"""Step 1: detect + encode face from image. Encoding hashed before going on-chain.

Calls dlib directly instead of depending on the `face_recognition` PyPI
package — that package's metadata pins `dlib` (source-only, no wheels) as a
dependency even when `dlib-bin` (prebuilt) is installed under a different
distribution name, which breaks builds on platforms without a C++ toolchain
(e.g. Heroku). This inlines the same logic face_recognition.api uses
(68-point landmarks -> 128-d ResNet encoding), against `dlib-bin` +
`face_recognition_models` only.
"""
import sys
import hashlib
import numpy as np
import dlib
import PIL.Image
import face_recognition_models

_face_detector = dlib.get_frontal_face_detector()
_pose_predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
_face_encoder = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())


def _load_image(path: str) -> np.ndarray:
    return np.array(PIL.Image.open(path).convert("RGB"))


def encode_face(image_path: str) -> np.ndarray:
    image = _load_image(image_path)
    face_rects = _face_detector(image, 1)
    if not face_rects:
        raise ValueError(f"No face detected in {image_path}")

    landmarks = _pose_predictor(image, face_rects[0])
    encoding = _face_encoder.compute_face_descriptor(image, landmarks, 1)
    return np.array(encoding)  # 128-d float vector


def face_hash(encoding: np.ndarray) -> str:
    """Deterministic hash of the face encoding."""
    rounded = np.round(encoding, 4)  # tolerate float noise
    return hashlib.sha256(rounded.tobytes()).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python face_id.py <image_path>")
        sys.exit(1)

    encoding = encode_face(sys.argv[1])
    print("Face encoded. 128-d vector, first 5 values:", encoding[:5])
    print("Face hash (sha256):", face_hash(encoding))
