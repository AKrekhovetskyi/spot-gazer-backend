# SpotGazer Backend

The DRF Backend service of the parking lot occupancy recognition system.
The repository is a part of a multi-service [SpotGather](https://github.com/AKrekhovetskyi/spot-gazer) system.

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
git clone https://github.com/AndriyKy/spot-gazer.git
cd spot-gazer-backend
```

Create an `.env` file from [`.env.sample`](../.env.sample) and set the necessary variables

```bash
mv .env.sample .env
```

Run [`build`](../build.sh) (for Linux based on Debian):

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

## 👨‍💻 Contribution

Make sure to install `pre-commit` and its hooks before making any commits:

```bash
pre-commit install --install-hooks
```

Run the tests with the following command:

```bash
poetry run pytest tests -vv -s -rA
```
