FROM python:alpine

RUN apk fix && \
    apk --no-cache --update add git pandoc gcc python3-dev build-base linux-headers
    # git: for cloning the repo when this container is used as gitlab runner
    # pandoc gcc python3-dev build-base linux-headers: dependencies of jupyter-book

RUN pip install --upgrade pip && \
    pip install jupyter-book
    # jupyter-book: required for converting ipynbs to static websites

WORKDIR /usr/src/app
ADD . .

RUN pip3 install .

CMD ["urnc", "/course"]

