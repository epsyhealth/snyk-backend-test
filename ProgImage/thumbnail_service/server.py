import os

from .transformation import transform_image
from .. import server
from ..server import app

server.transform_function = transform_image

app.register_blueprint(server.transform_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT"))
