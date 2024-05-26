#!/usr/bin/env bash

echo "Running autopep..."
find -type f -name '*.py' ! -path '*/migrations/*' -exec autopep8 --in-place --aggressive --aggressive '{}' \;
