#!/bin/bash

PYTHON_FILES="../src/*.py"

mkdir -p deskedit/

xgettext $PYTHON_FILES -o deskedit/deskedit.pot

