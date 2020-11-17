import concurrent.futures
import os
from urllib.parse import urljoin

from flask import request, Response, jsonify
from werkzeug.exceptions import BadRequest, NotFound, NotAcceptable

from .transformations import Transformations
from .. import MAX_UPLOAD_SIZE, TRANSFORM_WORKERS
from ..repository import ImageRepository
from ..server import app


@app.route("/images/<image_path>", methods=["GET"])
def download_image(image_path: str):
    repository = ImageRepository()
    try:
        contents, mimetype = repository.retrieve(image_path)

        if request.query_string:
            transformations = Transformations.from_query_params(request.args)
            contents, mimetype = transformations.apply(contents, mimetype)

        return Response(mimetype=mimetype, response=contents)
    except FileNotFoundError as error:
        raise NotFound(str(error))
    except ValueError as error:
        raise BadRequest(str(error))


@app.route("/images/", methods=["POST"])
def upload_image() -> Response:
    if request.content_length == 0:
        raise BadRequest("Image size must be greater than 0 bytes.")
    if request.content_length and request.content_length > MAX_UPLOAD_SIZE:
        raise BadRequest(f"Image size must not exceed {MAX_UPLOAD_SIZE:,} bytes.")

    repository = ImageRepository()

    try:
        image_path = repository.store(request.get_data())
    except ValueError as error:
        raise BadRequest(str(error))

    location = urljoin(request.url, image_path)
    response = jsonify(id=image_path, location=location)
    response.headers.update({"Location": location})
    response.status_code = 201
    return response


@app.route("/bulk/", methods=["POST"])
def bulk_transform() -> Response:
    if not request.is_json:
        raise NotAcceptable(f"Request must be application/json.")

    if not isinstance(request.json, dict):
        raise BadRequest("Request body must be a JSON object.")

    # Validate transformation params.
    bulk_transformations = {}
    for image_ref, params in request.json.items():
        if not params:
            continue

        try:
            transformations = Transformations.from_query_params(
                params, store_result=True
            )
            bulk_transformations[image_ref] = transformations
        except ValueError as error:
            raise BadRequest(f'Entry "{image_ref}": {error}')

    # Run transformations concurrently via the transformations services.
    transformation_results = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=TRANSFORM_WORKERS
    ) as executor:
        transformation_futures = {}
        for image_ref, transformations in bulk_transformations.items():
            future = executor.submit(transformations.apply, image_ref)
            transformation_futures[future] = image_ref

        for future in concurrent.futures.as_completed(transformation_futures):
            try:
                image_url, b = future.result()
                result = image_url.decode("utf-8")
            except Exception:
                # TODO: Expose errors like 400 and 404.
                result = {"error": "Transformation error."}
            finally:
                transformation_results[transformation_futures[future]] = result

    return jsonify(transformation_results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT"))
