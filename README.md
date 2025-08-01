# SpotGazer Backend

The DRF Backend service of the parking lot occupancy recognition system.
The repository is a part of a multi-service [SpotGather](https://github.com/AKrekhovetskyi/spot-gazer) system.

## ✨ Features

- JWT authentication ([default settings](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html) are used).
- Pagination at all endpoints (see the local [`REST_FRAMEWORK`](./django_core/settings.py) settings).

### Endpoints

- `api/schema/docs/` endpoint with Swagger documentation
- `api/video-stream-sources/` endpoint with CRUD operations to interact with video streams. Available query parameters:
  - `?active_only`: `true` or `false` - returns only video streams which are still working
  - `?mark_in_use_until`: UTC `datetime` (authentication required) - inner service parameter. Reserves video streams for a specified period of time
- `api/occupancy/` endpoint with CRUD operations to interact with occupancy of parking lots

## 🛠️ Prerequisites

To successfully setup backend, your system must meet the following requirements:

- Linux OS (tested on Debian-based distributions)
- Python 3.13
- [`poetry`](https://python-poetry.org/) and the [`poetry-dotenv-plugin`](https://github.com/pivoshenko/poetry-plugin-dotenv)

```bash
poetry self add poetry-dotenv-plugin
```

## 🔩 Installation

To run the backend service, execute the following commands in the Linux terminal:

```bash
git clone https://github.com/AKrekhovetskyi/spot-gazer.git
cd spot-gazer-backend
```

Create an `.env` file from [`.env.sample`](./.env.sample) and set the necessary variables

```bash
mv .env.sample .env
```

Run [`build`](./build.sh) (for Linux based on Debian):

```bash
./build.sh
```

Optionally, you can create a superuser and load test data:

```bash
poetry run python3 manage.py createsuperuser
poetry run python3 manage.py loaddata test_data.json
```

Then run SpotGazer:

```bash
poetry run python3 -m manage.py runserver
```

### 🥬 Tasks scheduling with Celery and Redis

First install and run Redis to start periodic tasks such as occupancy statistics aggregation by hours.
Execute the following command to start the Redis instance in a Docker container:

```bash
docker run -d --name redis -p 6379:6379 redis:8.0.3-bookworm
```

Start a Celery worker with a Celery Beat in the background:

```bash
celery -A django_core worker -B --loglevel info --logfile "$(pwd)/celery.log" --detach
```

You can stop the worker with the following command:

```bash
celery -A django_core control shutdown
```

Head over to the Django admin console ([http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)) after creating an admin user to schedule predefined periodic tasks.

## 🐳 Docker

Before you start building, create and populate the `.env` file with the required environment variable.

Use the following command to build a Docker container:

```bash
docker build --tag spot-gazer-backend:v1.0.0 .
```

Run the container with an exposed port:

```bash
docker run --rm -p 8000:8000 spot-gazer-backend:v1.0.0
```

## 💾 Storage

For **development and testing**, the environment uses a default **SQLite database**.
In **production**, the application connects to a **MySQL cluster** deployed on **AWS RDS**.

## 👨‍💻 Contribution

Make sure to install `pre-commit` and its hooks before making any commits:

```bash
pre-commit install --install-hooks
```

Run the tests with the following command:

```bash
poetry run python manage.py test tests
```
