from typing import Tuple, Optional

import requests
from flask import Request, Flask, jsonify, Blueprint, Response, request
from requests import RequestException
from werkzeug.exceptions import BadRequest, HTTPException, InternalServerError, NotFound

from ProgImage.repository import ImageRepository

app = Flask(__name__)


@app.errorhandler(HTTPException)
def generic_error_response(error):
    return jsonify({"error": f"{error.name}: {error.description}"}), error.code


@app.errorhandler(InternalServerError)
def internal_error_response(error):
    return jsonify({"error": error.description}), error.code


def parse_uri_or_binary(flask_request: Request) -> Tuple[bytes, str]:
    if flask_request.content_type and flask_request.content_type.startswith(
        "text/uri-list"
    ):
        # This will be a list of URLs with potential comments in lines beginning with #.
        # TODO: Handle encodings other than utf-8 or validate it at least.
        uri_list = [
            line.decode("utf-8").strip()
            for line in flask_request.data.replace(b"\r\n", b"\n").split(b"\n")
            if len(line) > 0 and line[0] != ord("#")
        ]
        if len(uri_list) < 1:
            raise BadRequest("At lest one URI must be in the list.")
        if len(uri_list) > 1:
            raise BadRequest("Multiple URIs per request are not supported.")

        try:
            image_response = requests.get(uri_list[0])
            image_response.raise_for_status()
            original_image = image_response.content
            content_type = image_response.headers.get("Content-Type")
        except RequestException as error:
            raise BadRequest(f"Unable to download image: {error}") from error
    else:
        original_image = flask_request.data
        content_type = flask_request.content_type

    if not content_type:
        raise BadRequest("Couldn't obtain the MIME type of the original image")

    return original_image, content_type


# Just placeholder.
def zero_transform(
    contents: bytes, mimetype: str, params: Optional[dict] = None
) -> bytes:
    return contents


transform_function = zero_transform
transform_blueprint = Blueprint("transform_blueprint", __name__)


@transform_blueprint.route("/transform/<image_path>", methods=["GET"])
def transform_from_repository(image_path: str):
    try:
        original_image, content_type = ImageRepository().retrieve(image_path)
    except FileNotFoundError as error:
        raise NotFound(error)

    try:
        transformed_image = transform_function(
            original_image, content_type, request.args
        )
    except ValueError as error:
        raise BadRequest(error)

    if request.args.get("store_result"):
        transformed_image = ImageRepository().store(transformed_image)
        content_type = "text/plain"

    return Response(
        response=transformed_image, status=200, headers={"Content-Type": content_type},
    )


@transform_blueprint.route("/transform/", methods=["POST"])
def transform_from_image():
    original_image, content_type = parse_uri_or_binary(request)

    # TODO: Refactor this to remove the duplicate code.
    try:
        transformed_image = transform_function(
            original_image, content_type, request.args
        )
    except ValueError as error:
        raise BadRequest(error)

    if request.args.get("store_result"):
        transformed_image = ImageRepository().store(transformed_image)
        content_type = "text/plain"

    return Response(
        response=transformed_image, status=200, headers={"Content-Type": content_type},
    )
