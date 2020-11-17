import os

from PIL import Image

MAX_UPLOAD_SIZE = os.getenv("MAX_UPLOAD_SIZE", 10_000_000)  # Bytes.
# Maximum number of concurrent transform operations.
TRANSFORM_WORKERS = os.getenv("TRANSFORM_WORKERS", 10)


def get_format_for_mimetype(mimetype: str) -> str:
    Image.init()  # Explicitly initialise PIL so it knows all available formats.

    for image_format, image_mimetype in Image.MIME.items():
        if image_mimetype == mimetype:
            return image_format

    raise ValueError(f'MIME type "{mimetype}" is not supported.')
