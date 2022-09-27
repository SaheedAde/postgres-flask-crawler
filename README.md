# postgres-flask-crawler

This is a simple Web Crawler App using Flask, Postgres, gunicorn and docker-compose.

## Installation

Step 0: Use [docker-compose](https://docs.docker.com/compose/) to install and start.
```bash
$ docker-compose build
$ docker-compose up
```

## Usage

Step 1: Initialise the database by hitting the endpoint
```bash
$ curl localhost:8088
```

Step 2: Crawl lucierne and store events in db
```bash
$ curl -X POST localhost:8088/crawl_events/
```

Step 3: Retrieve stored events
```bash
$ curl localhost:8088/get_events_in_db/
```
