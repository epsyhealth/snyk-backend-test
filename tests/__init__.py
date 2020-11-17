import os
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"

os.environ["STORAGE"] = "s3"
os.environ["S3_BUCKET"] = "test-bucket"

os.environ["FLASK_DEBUG"] = "1"
os.environ["IS_OFFLINE"] = "1"

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"
os.environ["AWS_REGION"] = "eu-west-2"
