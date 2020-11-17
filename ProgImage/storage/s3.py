import os
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError

from . import generate_id

bucket_name = os.getenv("S3_BUCKET", "matepager-progimage")
s3_bucket = boto3.resource("s3").Bucket(bucket_name)


def _get_key(image_id: str) -> str:
    return f"images/{image_id}"


def store(contents: bytes, mimetype: str, image_id: Optional[str] = None) -> str:
    if not image_id:
        image_id = generate_id()

    s3_bucket.put_object(
        Key=_get_key(image_id), Body=contents, ContentType=mimetype,
    )

    return image_id


def retrieve(image_id: str) -> Tuple[bytes, str]:
    try:
        s3_object = s3_bucket.Object(_get_key(image_id))
        response = s3_object.get()
        return response["Body"].read(), response["ContentType"]
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            raise FileNotFoundError("Image doesn't exist.") from error
        else:
            raise
