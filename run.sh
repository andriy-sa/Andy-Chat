#!/bin/bash

set -e
LOGFILE=/var/log/gunicorn/flask.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=1
# user/group to run as
USER=root
GROUP=sudo
PORT=5000
cd /home/ubuntu/andy-chat/Andy-Chat/
source ../bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR

exec gunicorn --worker-class eventlet run:application -w $NUM_WORKERS \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE 2>>$LOGFILE \
  --bind 127.0.0.1:$PORT