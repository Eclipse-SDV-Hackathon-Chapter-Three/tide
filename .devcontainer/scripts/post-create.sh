#!/bin/bash

if ! grep -q "bashrc_addition" ~/.bashrc && [[ -f "${WORKSPACE_FOLDER}/.devcontainer/scripts/bashrc_addition.sh" ]]; then
    echo "source ${WORKSPACE_FOLDER}/.devcontainer/scripts/bashrc_addition.sh" >> ~/.bashrc
fi
