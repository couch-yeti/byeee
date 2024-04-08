# Use the AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.10

# Install Poetry or other dependencies if necessary
ENV POETRY_VERSION=1.4.0
RUN pip install "poetry==$POETRY_VERSION"
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /var/task

# Argument to specify which Lambda source directory to include
ARG FUNCTION_DIR

# Copy shared and specific lambda source code
COPY ./src/common ./common
COPY ./src/${FUNCTION_DIR} ./${FUNCTION_DIR}

# Install Python dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-dev

# Set the working directory to the function directory
WORKDIR /var/task/${FUNCTION_DIR}

# You may specify your handler in CDK or through AWS Console
CMD [ "handler.lambda_handler" ]