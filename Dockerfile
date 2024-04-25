# Use the AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.10

# Install Poetry or other dependencies if necessary
ENV POETRY_VERSION=1.4.0
RUN pip install "poetry==$POETRY_VERSION"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONPATH "${PYTHONPATH}:${LAMBDA_TASK_ROOT}"

# Copy shared and specific lambda source code
COPY src ${LAMBDA_TASK_ROOT}

# Install Python dependencies
COPY pyproject.toml poetry.lock ${LAMBDA_TASK_ROOT}

WORKDIR ${LAMBDA_TASK_ROOT}
RUN poetry install --no-root --only main --no-ansi --no-interaction

# You may specify your handler in CDK or through AWS Console
CMD ["overwritten in components"]