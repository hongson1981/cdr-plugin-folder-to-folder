FROM    python:3.10-rc-alpine3.13
RUN     apk update && apk upgrade && \
        apk add --no-cache bash git openssh gcc libc-dev linux-headers

# the following ENV need to be present

ARG S3FS_VERSION=v1.82

RUN apk --update add --virtual build-dependencies \
        build-base alpine-sdk \
        fuse fuse-dev \
        automake autoconf git \
        libressl-dev  \
        curl-dev libxml2-dev  \
        ca-certificates

# RUN apk del .build-dependencies

RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git && \
    cd s3fs-fuse \
    git checkout tags/${S3FS_VERSION} && \
    ./autogen.sh && \
    ./configure --prefix=/usr && \
    make && \
    make install

WORKDIR /app
# Add wait-for-it
ADD    https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh wait-for-it.sh
RUN     chmod +x wait-for-it.sh
COPY    cdr_plugin_folder_to_folder/requirements.txt .
RUN     pip install -r requirements.txt
ADD     cdr_plugin_folder_to_folder ./cdr_plugin_folder_to_folder
COPY    .env.sample ./cdr_plugin_folder_to_folder/.env
ENV     PYTHONPATH=.
CMD     python cdr_plugin_folder_to_folder/api/Server.py
EXPOSE  8880