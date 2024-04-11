#
# Build: docker build -t hocr-tools-app .
# Start: docker run -it --rm -v ${PWD}:/usr/src/app hocr-tools-app bash
# Test: ./test/tsht
#

FROM python:3
ENV PYTHONIOENCODING utf8

RUN apt-get update && apt-get install -y --no-install-recommends pdfgrep \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN python -m pip install .

CMD python -m unittest discover --verbose --start-directory tests/
