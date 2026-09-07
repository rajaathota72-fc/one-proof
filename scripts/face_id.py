"""
Step 1: Face detection + encoding from an input image.

Uses `face_recognition` (dlib-based). Encodes the face into a 128-d vector
used later as a fingerprint (hashed before going on-chain, never stored raw).
"""
import sys
import hashlib
import numpy as np
import face_recognition


def encode_face(image_path: str) -> np.ndarray:
    image = face_recognition.load_image_file(image_path)
    locations = face_recognition.face_locations(image)
    if not locations:
        raise ValueError(f"No face detected in {image_path}")
    encodings = face_recognition.face_encodings(image, known_face_locations=locations)
    return encodings[0]  # 128-d float vector for the first/primary face


def face_hash(encoding: np.ndarray) -> str:
    """Deterministic hash of the face encoding, for on-chain storage."""
    rounded = np.round(encoding, 4)  # tolerate float noise
    return hashlib.sha256(rounded.tobytes()).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python face_id.py <image_path>")
        sys.exit(1)

    encoding = encode_face(sys.argv[1])
    print("Face encoded. 128-d vector, first 5 values:", encoding[:5])
    print("Face hash (sha256):", face_hash(encoding))
