FROM python:alpine

RUN apk fix && \
    apk --no-cache --update add git 

WORKDIR /usr/src/app
ADD . .

RUN pip3 install .

CMD ["urnc", "/course"]

