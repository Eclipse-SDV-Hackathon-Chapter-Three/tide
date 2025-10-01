FROM mcr.microsoft.com/devcontainers/python:dev-3.13
ARG USERNAME=vscode

RUN pip install pipenv

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y nodejs