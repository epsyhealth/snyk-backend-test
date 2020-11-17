ProgImage.com
============

Engineering challenge solution (attempt).

Description
-----------

This project contains a number of microservices that implement an image storage and manipulation engine with an API. It is written in Python 3 and uses Docker containers for each microservice.

The storage engine is modular and it can be configured to use plain file storage (for shared volumes or network file systems to share data between nodes) or cloud storage on AWS S3. New storage engines are fairly simple to implement.

The transformations are modular too, it is quick and easy to implement and roll out a new transformation feature.

API Docs
--------

There're more details on the functionality of each endpoint in the OpenAPI 3.0 docs in the openapi.yaml file.

Installation
------------

The microservices stack can be managed locally via [docker-compose](https://docs.docker.com/compose/). To build the containers run `docker-compose build` and to start them run `docker-compose up`.

Testing
-------

There are a number of pytest tests to ensure that the base functionality of uploading and download images and converting them to a different format.

Running Locally
---------------

The S3 storage engine requires AWS credentials for boto3. One quick way to provide these is by running `docker-compose up` along with `aws-vault exec` for example:

```
aws-vault exec profilename -- docker-compose up
```
