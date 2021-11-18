# simple url shortener
This project uses [FastAPI](https://fastapi.tiangolo.com) and [SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/) to create a simple URL shortener based on [these](https://github.com/arcotech-services/st-backend-challenge/blob/main/desafios/encurtador-de-url.md) specs.

This uses a [sqlite](https://www.sqlite.org/index.html) for Test database and [POSTGRESQL](https://www.postgresql.org/) for production.

The shortener creates 8 character keys for urls sent via POST!

## Running with docker-compose

To run this project, just use [docker-compose](https://docs.docker.com/compose/) and do:

```
docker-compose up --build
```

This will make available in your local machine on port `8000` the service.


## Schema and Documentation
You can always see a **live** version of the API schema following OpenAPI specs at `/docs` on the live service.