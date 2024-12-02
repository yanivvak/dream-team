#!/bin/bash
set -e

sudo apt update
pip install --upgrade pip 
pip install -r src/requirements.txt
pip install playwright
playwright install --with-deps chromium

cd src 
git clone --depth 1 https://github.com/microsoft/autogen.git 
cd autogen/python/packages/autogen-magentic-one
pip install -e .