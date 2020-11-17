import json
import os
from pathlib import Path
from typing import Optional, Tuple

from . import generate_id

storage_path = Path(os.getenv("FILE_PATH", "/var/ProgImage"))
images_path = storage_path / "images"
metadata_path = storage_path / "metadata"

for _path in (storage_path, images_path, metadata_path):
    if not _path.exists():
        os.makedirs(str(_path))


def _get_file_path(image_id: str) -> Path:
    return storage_path / image_id


def _get_metadata_path(image_id: str) -> Path:
    return metadata_path / image_id


def _get_file_metadata(image_id: str) -> dict:
    with open(metadata_path / image_id, "r", encoding="utf-8") as fp:
        return json.loads(fp.read())


def store(contents: bytes, mimetype: str, image_id: Optional[str] = None) -> str:
    if not image_id:
        image_id = generate_id()

    with open(str(_get_file_path(image_id)), "wb") as fp:
        fp.write(contents)

    with open(str(_get_metadata_path(image_id)), "w", encoding="utf-8") as fp:
        fp.write(json.dumps({"Content-Type": mimetype}))

    return image_id


def retrieve(image_id: str) -> Tuple[bytes, str]:
    file_path = _get_file_path(image_id)
    if not file_path.exists():
        raise FileNotFoundError("Image doesn't exist.")

    metadata = _get_file_metadata(image_id)

    with open(str(file_path), "rb") as fp:
        return fp.read(), metadata["Content-Type"]
