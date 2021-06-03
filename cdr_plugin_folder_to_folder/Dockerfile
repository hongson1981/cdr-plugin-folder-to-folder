FROM    python:3.9.3-alpine3.12
RUN     apk update && apk upgrade && \
        apk add --no-cache bash git openssh gcc libc-dev linux-headers

# the following ENV need to be present
ENV IAM_ROLE=none
ENV MOUNT_POINT=/var/s3
VOLUME /var/s3

ARG S3FS_VERSION=v1.79

RUN apk --update add fuse alpine-sdk automake autoconf libxml2-dev fuse-dev curl-dev git bash;
RUN git clone https://github.com/s3fs-fuse/s3fs-fuse.git; \
 cd s3fs-fuse; \
 git checkout tags/${S3FS_VERSION}; \
 ./autogen.sh; \
 ./configure --prefix=/usr; \
 make; \
 make install; \
 rm -rf /var/cache/apk/*;

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