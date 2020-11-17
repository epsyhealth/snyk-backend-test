import os
from importlib import import_module
from io import BytesIO
from mimetypes import guess_extension, guess_type
from pathlib import Path
from typing import Union, Tuple

from PIL import Image, UnidentifiedImageError

from . import MAX_UPLOAD_SIZE, get_format_for_mimetype

storage_engine_type = os.getenv("STORAGE", "file")
try:
    storage_engine = import_module(
        name=f".storage.{storage_engine_type}", package="ProgImage"
    )
except ModuleNotFoundError as error:
    raise ValueError("Invalid storage engine type. Choose one from: file, s3")


class ImageRepository:
    def __init__(self):
        self.storage = storage_engine

    def store(self, contents: bytes) -> str:
        if len(contents) > MAX_UPLOAD_SIZE:
            raise ValueError(f"Image size must not exceed {MAX_UPLOAD_SIZE:,} bytes.")

        try:
            image = Image.open(BytesIO(contents))
            mimetype = Image.MIME[image.format]
            image_id = self.storage.store(contents=contents, mimetype=mimetype)
        except UnidentifiedImageError:
            raise ValueError("Uploaded file is not an image or format is unknown.")

        return image_id + (guess_extension(mimetype) or "")

    def retrieve(self, image_path: Union[str, Path]) -> Tuple[bytes, str]:
        image_path = Path(image_path)
        requested_mimetype, _ = guess_type(image_path)
        if not requested_mimetype:
            raise ValueError("Requested MIME type is unknown.")

        contents, original_mimetype = self.storage.retrieve(
            image_id=image_path.with_suffix("")
        )
        if requested_mimetype == original_mimetype:
            return contents, original_mimetype

        # Convert image if the requested MIME type is different than the original.
        requested_format = get_format_for_mimetype(requested_mimetype)
        converted_contents = BytesIO()
        with Image.open(BytesIO(contents)) as image:
            image.save(converted_contents, format=requested_format)

        return bytes(converted_contents.getvalue()), requested_mimetype
