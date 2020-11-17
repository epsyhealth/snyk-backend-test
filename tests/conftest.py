import boto3
import pytest
from moto import mock_s3

from tests import FIXTURE_DIR


@pytest.fixture
def mock_s3_storage():
    with mock_s3():
        s3 = boto3.client("s3", region_name="eu-west-2")
        s3.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )

        yield s3


@pytest.fixture
def jpeg_fixture_1():
    with open(FIXTURE_DIR / "test1.jpg", "rb") as fp:
        yield fp.read()


@pytest.fixture
def s3_jpeg_fixture_1(jpeg_fixture_1, mock_s3_storage):
    mock_s3_storage.put_object(
        Bucket="test-bucket",
        ContentType="image/jpeg",
        Key="images/test-file-1",
        Body=jpeg_fixture_1,
    )
