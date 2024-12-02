#!/bin/bash
set -e

sudo apt update
pip install --upgrade pip 
pip install -r src/requirements.txt
pip install playwright
playwright install --with-deps chromium