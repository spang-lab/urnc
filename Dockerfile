# Version: see pyproject.toml
# Base: https://hub.docker.com/r/jupyter/datascience-notebook/tags
# Build: docker build -t thespanglab/urnc:latest .
# Run: docker run -it --rm thespanglab/urnc:latest
# Push:
#   docker login -u thespanglab -p $DOCKERHUB_TOKEN docker.io
#   docker push "thespanglab/urnc:latest"
FROM python:alpine

RUN apk fix && \
    apk --no-cache --update add git bash pandoc gcc python3-dev build-base linux-headers
    # git: for cloning the repo when this container is used as gitlab runner
    # bash: for running bash scripts when this container is used as gitlab runner
    # pandoc gcc python3-dev build-base linux-headers: dependencies of jupyter-book

RUN pip install --upgrade pip && \
    pip install jupyter-book
    # jupyter-book: required for converting ipynbs to static websites

WORKDIR /usr/src/app
ADD . .

RUN pip3 install .

CMD ["urnc", "ci"]
