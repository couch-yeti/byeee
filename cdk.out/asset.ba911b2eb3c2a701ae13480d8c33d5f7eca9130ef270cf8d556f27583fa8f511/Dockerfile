# Use the AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.10

ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/local/bin/aws-lambda-rie
RUN chmod +x /usr/local/bin/aws-lambda-rie

# Install Poetry or other dependencies if necessary
ENV POETRY_VERSION=1.4.0
RUN pip install "poetry==$POETRY_VERSION"
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /var/task

# Argument to specify which Lambda source directory to include
ARG FUNCTION_DIR

# Copy shared and specific lambda source code
COPY ./src/common ${LAMBDA_TASK_ROOT}/common
COPY ./src/${FUNCTION_DIR} ${LAMBDA_TASK_ROOT}

# Install Python dependencies
COPY pyproject.toml poetry.lock* ${LAMBDA_TASK_ROOT}
RUN poetry install --no-dev --no-root

# You may specify your handler in CDK or through AWS Console
CMD [ "handler.lambda_handler" ]