from io import BytesIO
from typing import Optional

from PIL import Image

from ProgImage import get_format_for_mimetype


def transform_image(
    contents: bytes, mimetype: str, params: Optional[dict] = None
) -> bytes:
    # TODO: Validate thumbnail size
    # TODO: Check args and return 400 for unknown ones
    if params and params.get("size"):
        size = tuple(int(dim.strip()) for dim in params["size"].split("*"))
    else:
        size = (200, 200)

    transformed_contents = BytesIO()
    image_format = get_format_for_mimetype(mimetype)
    with Image.open(BytesIO(contents)) as image:
        image.thumbnail(size)
        image.save(transformed_contents, format=image_format)

    return transformed_contents.getvalue()
