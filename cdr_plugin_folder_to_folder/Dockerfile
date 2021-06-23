FROM    python:3.10.0b1-alpine3.12
RUN     apk update && apk upgrade && \
        apk add --no-cache bash git openssh gcc libc-dev linux-headers

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