#!/usr/bin/sh

set -xe

mypy
./test.py
pylint *.py
