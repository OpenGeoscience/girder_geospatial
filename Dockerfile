FROM geographica/gdal2:2.3.0

MAINTAINER Kitware, Inc. <kitware@kitware.com>

# Install python3.6
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get -y update && \
    apt-get -y install python3.6

RUN apt-get install -y python-pip git curl apt-transport-https python3.6-dev

# Install mongodb
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5 && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.6.list && \
    apt-get -y update && apt-get install -y mongodb-org && \
    mkdir -p /data/db

RUN pip install tox

# This hack is needed to install gdal python bindings
RUN curl 'https://raw.githubusercontent.com/OSGeo/gdal/release/2.3/gdal/port/cpl_vsi_error.h' -o /usr/local/include/cpl_vsi_error.h
