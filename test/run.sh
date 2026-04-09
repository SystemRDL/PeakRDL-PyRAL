#!/bin/bash

set -e

cd "$(dirname "$0")"

# Initialize venv
#rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Install dut
pip install systemrdl-compiler
pip install -e "../pkg-runtime"
pip install -e "../pkg-exporter[cli]"

# Run lint
pylint --rcfile pylint.rc ../pkg-exporter/src/peakrdl_pyral
pylint --rcfile pylint.rc ../pkg-runtime/src/peakrdl_pyral_runtime

# Run static type checking
mypy ../pkg-exporter/src/peakrdl_pyral
mypy ../pkg-runtime/src/peakrdl_pyral_runtime

# Run unit tests
pytest --cov=peakrdl_pyral --cov=peakrdl_pyral_runtime

# Generate coverage report
coverage html -i -d htmlcov
