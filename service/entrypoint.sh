#!/bin/bash

# Start the first process
gunicorn -c gunicorn.conf.py main:app &

# Start the second process
python cleanup.py &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?