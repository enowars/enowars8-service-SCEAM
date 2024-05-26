#!/usr/bin/env bash

echo "Running autopep..."
find -type f -name '*.py'  -exec autopep8 --in-place --aggressive --aggressive '{}' \;
echo "Running autoflake..."
find -type f -name '*.py'  -exec autoflake --in-place --remove-unused-variables  --remove-all-unused-imports '{}' \;
echo "Running pyflakes..."
find -type f -name '*.py'  -exec pyflakes '{}' \;
