import logging
import os
from enum import Enum, auto
from typing import Any, Dict, Union, Tuple, Optional
from urllib.parse import urljoin

import requests
from requests import HTTPError


class ImageTransformation(Enum):
    THUMBNAIL = auto()
    ROTATE = auto()


transformation_urls = {
    ImageTransformation.THUMBNAIL: os.getenv("THUMBNAIL_TRANSFORMATION_URL"),
    ImageTransformation.ROTATE: os.getenv("ROTATE_TRANSFORMATION_URL"),
}


class Transformations:
    def __init__(
        self,
        transformations: Dict[ImageTransformation, Dict[str, Any]],
        store_result: bool = False,
    ):
        self.transformations = transformations
        self.store_result = store_result

    @staticmethod
    def from_query_params(params: dict, **kwargs) -> "Transformations":
        transformations = {}
        for param, option_value in params.items():
            if param.count("-") != 1:
                raise ValueError(f'Invalid transformation parameter: "{param}"')
            command, option_name = param.split("-")
            try:
                t = ImageTransformation[command.upper()]
                if t not in transformations:
                    transformations[t] = {}
                transformations[t][option_name] = option_value
            except KeyError:
                raise ValueError(f'Unknown transformation command: "{command}"')

        return Transformations(transformations, **kwargs)

    def apply(
        self, image: Union[bytes, str], mimetype: Optional[str] = None
    ) -> Tuple[bytes, str]:
        session = requests.Session()
        session.timeout = (3.05, 20)

        for index, (transformation, options) in enumerate(self.transformations.items()):
            url = transformation_urls[transformation]
            if not url:
                logging.getLogger(__name__).warning(f"No URL set for {transformation}")
                continue

            url = urljoin(url, "transform/")
            transform_mimetype = mimetype

            if isinstance(image, bytes):
                method = "POST"
                data = image
                if not mimetype:
                    raise ValueError(
                        "MIME type is required when source is raw image data"
                    )
            elif isinstance(image, str):
                if image.startswith("http://") or image.startswith("https://"):
                    method = "POST"
                    transform_mimetype = "text/uri-list"
                    data = image.encode("utf-8")
                else:
                    method = "GET"
                    data = None
                    url = urljoin(url, image)
            else:
                raise ValueError("Invalid data type passed as image")

            image, mimetype = self._apply_transition(
                session=session,
                method=method,
                url=url,
                params=options,
                data=data,
                mimetype=transform_mimetype,
                store_result=self.store_result
                and index == len(self.transformations) - 1,
            )

        return image, mimetype

    @staticmethod
    def _apply_transition(
        session: requests.Session,
        method: str,
        url: str,
        params: dict,
        data: bytes,
        mimetype: Optional[str],
        store_result: bool = False,
    ) -> Tuple[bytes, str]:
        # TODO: Use tenacity to retry on status codes where it makes sense (e.g., 503)
        if store_result:
            params["store_result"] = "1"

        try:
            args = dict(method=method, url=url, params=params, data=data,)
            if mimetype:
                args["headers"] = {"Content-Type": mimetype}

            response = session.request(**args)
            response.raise_for_status()
            return response.content, response.headers["Content-Type"]
        except HTTPError as error:
            if error.response is not None and error.response.status_code == 400:
                raise ValueError(f"Invalid transformation: {error}") from error
            raise TransformationError(error) from error
        except Exception as error:
            raise TransformationError(error) from error


class TransformationError(OSError):
    pass
