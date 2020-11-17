from io import BytesIO
from typing import Optional

from PIL import Image

from ProgImage import get_format_for_mimetype

transpose_option_mapping = {
    90: Image.ROTATE_90,
    180: Image.ROTATE_180,
    270: Image.ROTATE_270,
}


def transform_image(
    contents: bytes, mimetype: str, params: Optional[dict] = None
) -> bytes:
    # TODO: Validate image rotation and transposition angle
    # TODO: Expose more options like "expand" and "center"
    transpose = int(params["transpose"]) if params and params.get("transpose") else 0
    angle = int(params["angle"]) if params and params.get("angle") else 0

    transformed_contents = BytesIO()
    image_format = get_format_for_mimetype(mimetype)
    with Image.open(BytesIO(contents)) as image:
        if transpose:
            try:
                image = image.transpose(transpose_option_mapping[transpose])
            except KeyError:
                raise ValueError(
                    "Invalid transpose option. Must be one of: 90, 180, 270"
                )
        if angle:
            image = image.rotate(angle)

        image.save(transformed_contents, format=image_format)

    return transformed_contents.getvalue()
