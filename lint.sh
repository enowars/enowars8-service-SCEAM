#!/bin/bash

# Find all .py files recursively and apply autopep8
# in get bash run this command: sh lint.sh
find . -type f -name "*.py" -exec autopep8 --in-place {} \;




 