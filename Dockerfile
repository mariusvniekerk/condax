FROM python:3.8

ADD . /src

WORKDIR /src

RUN pip install .

RUN condax ensure-path

RUN condax install jq

ENV PATH="/root/.local/bin:$PATH"
RUN jq --help