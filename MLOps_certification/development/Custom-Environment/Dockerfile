# This is the default base image for use with user models and workflows.
# It contains a variety of common useful data-science packages and tools.
FROM python:3.7-slim
ENV LC_ALL=en_US.UTF-8 TERM=xterm COLS=132 ROWS=43 DEBIAN_FRONTEND=noninteractive

# Package versions are the latest as of when this script was last updated,
# unless otherwise noted.
RUN pip3 install \
    wheel==0.32.3

# Install the list of core requirements, e.g. sklearn, numpy, pandas, flask.
# **Don't modify this file!**
COPY dr_requirements.txt dr_requirements.txt
RUN pip3 install --only-binary :all: -r dr_requirements.txt --no-cache-dir && \
    rm -rf dr_requirements.txt

# Install the list of custom Python requirements, e.g. keras, xgboost, etc.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir && \
    rm -rf requirements.txt
