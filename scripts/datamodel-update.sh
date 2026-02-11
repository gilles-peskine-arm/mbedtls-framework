#!/bin/sh

#set -eu

: ${PYTHON:=python}

## update_json SCHEMA.json OUTPUT.py
update_json () {
    "$PYTHON" -m datamodel_code_generator \
              --input-file-type=jsonschema --input "$1" \
              --output-model-type=pydantic_v2.BaseModel --output "$2"
}

## update_wycheproof .../wycheproof
update_wycheproof () {
    mkdir -p "$MODELS_DIR/wycheproof"
    for x in "$1/schemas"/*schema*.json; do
        y=${x##*/}; y=${y%.*}.py
        update_json "$x" "$MODELS_DIR/wycheproof/$y"
    done
}

# Ignore warnings that are only of interest to the maintainers of the
# third-party Python libraries that we use.
export PYTHONWARNINGS=ignore::DeprecationWarning,ignore::FutureWarning

MODELS_DIR="$(dirname "$0")"/mbedtls_framework/data_models

update_wycheproof "$1"
