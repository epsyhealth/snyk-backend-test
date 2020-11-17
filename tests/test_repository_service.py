import json
import os
from io import BytesIO

import pytest
from PIL import Image


class TestUpload:
    def test_upload_works(self, mock_s3_storage, jpeg_fixture_1):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.post("/images/", data=jpeg_fixture_1)
            assert response.status_code == 201, response.data
            response_json = json.loads(response.data)
            assert "id" in response_json
            assert "location" in response_json
            assert response_json["location"].endswith(response_json["id"])

        list_result = mock_s3_storage.list_objects(Bucket="test-bucket")
        all_objects = list_result["Contents"]
        assert len(all_objects) == 1
        assert (
            all_objects[0]["Key"]
            == "images/" + os.path.splitext(response_json["id"])[0]
        )

        uploaded_image = mock_s3_storage.get_object(
            Bucket="test-bucket", Key=all_objects[0]["Key"]
        )
        assert uploaded_image["ContentType"] == "image/jpeg"
        assert uploaded_image["ContentLength"] == 619148
        assert uploaded_image["Body"].read() == jpeg_fixture_1

    def test_upload_returns_400_for_empty_data(self, mock_s3_storage):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.post("/images/", data=b"")
            assert response.status_code == 400, response.data

    def test_upload_returns_400_for_too_large_image(self, mock_s3_storage, monkeypatch):
        from ProgImage.repository_service import server
        from ProgImage.repository_service.server import app

        monkeypatch.setattr(server, "MAX_UPLOAD_SIZE", 10)

        # Test Content-Length check
        with app.test_client() as client:
            response = client.post(
                "/images/", data=b"1234", headers={"Content-Length": 11}
            )
            assert response.status_code == 400, response.data

        # Test if the Content-Length check can be bypassed
        with app.test_client() as client:
            response = client.post(
                "/images/", data=b"12345678901", headers={"Content-Length": 1}
            )
            assert response.status_code == 400, response.data
            assert b"must not exceed 10 bytes" in response.data

    def test_upload_returns_400_for_non_image(self, mock_s3_storage):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.post("/images/", data=b"I'm a text file")
            assert response.status_code == 400, response.data


class TestDownload:
    @pytest.mark.usefixtures("s3_jpeg_fixture_1")
    def test_download_works(self, jpeg_fixture_1):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.get("/images/test-file-1.jpg")
            assert response.status_code == 200, response.data
            assert response.headers["Content-Type"] == "image/jpeg"
            assert response.data == jpeg_fixture_1

    @pytest.mark.usefixtures("mock_s3_storage")
    def test_unknown_file_results_in_404(self):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.get("/images/unknown.jpg")
            assert response.status_code == 404, response.data


class TestFormatConversion:
    @pytest.mark.usefixtures("s3_jpeg_fixture_1")
    def test_conversion_works(self):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.get("/images/test-file-1.png")
            assert response.status_code == 200, response.data
            assert response.headers["Content-Type"] == "image/png"

            image = Image.open(BytesIO(response.data))
            assert image.format == "PNG"
            assert image.size == (2000, 2000)

    @pytest.mark.usefixtures("s3_jpeg_fixture_1")
    def test_unsupported_file_format_results_in_400(self):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.get(f"/images/test-file-1.txt")
            assert response.status_code == 400, response.data
            assert b"not supported" in response.data
            assert b"text/plain" in response.data

    @pytest.mark.usefixtures("s3_jpeg_fixture_1")
    @pytest.mark.parametrize(
        "image_path", ["test-file-1", "test-file-1.", "test-file-1.asdasd"]
    )
    def test_unknown_file_format_results_in_400(self, image_path):
        from ProgImage.repository_service.server import app

        with app.test_client() as client:
            response = client.get(f"/images/{image_path}")
            assert response.status_code == 400, response.data
            assert b"is unknown" in response.data
