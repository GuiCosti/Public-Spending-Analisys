#FROM ubuntu:18.04
FROM python:3.8-slim

## Conda setup
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local 

ENV PATH /opt/conda/bin:$PATH

##Setup
ENV PORT 5000
EXPOSE ${PORT}

# Copy database & configurations to root folder
COPY database.db .
COPY configurations.yml .

# Copy all content from /app folder to /app folder inside the container
COPY /app/ /app

# Change container current directory to /app
WORKDIR /app


ENV PATH /root/.local/bin:$PATH

# Run Install file that is inside /app -> /app/Install 
# The Install file contains a command to run "conda install --yes --file requirements.txt" for installing python requirements
RUN chmod +x install && ./install

ENTRYPOINT ["/bin/sh", "-c", "python __init__.py ${PORT}"]

