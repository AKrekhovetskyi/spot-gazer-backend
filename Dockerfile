ARG WORKDIR_ROOT="/opt"
ARG PYTHON_VERSION="3.13"

FROM python:${PYTHON_VERSION}-slim AS builder

ARG WORKDIR_ROOT

# Set environment variables to optimize Python
ENV PIP_NO_CACHE_DIR=off \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=2.1.3 \
    # Make poetry install to this location
    POETRY_HOME="${WORKDIR_ROOT}/poetry" \
    # Make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # Do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # This is where our requirements + virtual environment will live
    PYSETUP_PATH="${WORKDIR_ROOT}/pysetup" \
    VENV_PATH="${WORKDIR_ROOT}/pysetup/.venv"


# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # Deps for installing poetry
    curl \
    # Deps for building python deps (https://pypi.org/project/mysqlclient/)
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev

# Install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR "${WORKDIR_ROOT}/pysetup"
COPY poetry.lock pyproject.toml ./

# Install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install
RUN poetry self add poetry-plugin-dotenv@latest

FROM python:${PYTHON_VERSION}-slim

ARG WORKDIR_ROOT
ARG PYTHON_VERSION

# Set environment variables to optimize Python
ENV PATH="$WORKDIR_ROOT/poetry/bin:$WORKDIR_ROOT/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN useradd -m -r appuser && \
    mkdir -p "${WORKDIR_ROOT}/app" && \
    chown -R appuser "${WORKDIR_ROOT}/app"

# Set the working directory
WORKDIR "${WORKDIR_ROOT}/app"
# Copy application code
COPY --chown=appuser:appuser . .

# Copy the Python dependencies from the builder stage
COPY --from=builder "${WORKDIR_ROOT}/poetry" "${WORKDIR_ROOT}/poetry"
RUN poetry env use -- python${PYTHON_VERSION}

COPY --from=builder "$WORKDIR_ROOT/pysetup/.venv/lib/python${PYTHON_VERSION}/site-packages/" "$WORKDIR_ROOT/app/.venv/lib/python${PYTHON_VERSION}/site-packages/"

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

CMD ["${WORKDIR_ROOT}/app/entrypoint.sh"]
