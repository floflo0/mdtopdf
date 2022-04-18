#!/bin/sh

set -e

mypy
./test.py
pylint *.py

