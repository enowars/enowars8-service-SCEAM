#!/bin/bash

# Start the first process
gunicorn --bind 0.0.0.0:8008 main:app &

# Start the second process
python cleanup.py &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?