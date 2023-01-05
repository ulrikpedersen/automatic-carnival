# Lets name this image: ubuntu2204-pytango-dev
FROM ubuntu:22.04
RUN apt-get update -q && \
    apt-get install -y -q sudo \
    build-essential python3 python3-pip python3-venv gdb \
    lcov doxygen clang-tidy-12 cppcheck \
    libboost-python-dev
RUN update-alternatives --install /usr/bin/clang-tidy clang-tidy /usr/bin/clang-tidy-12 120
# Create a non-root account 'developer' without a password
# and give this account sudo access
RUN useradd --create-home --shell /bin/bash developer \
    && adduser developer sudo

# Ensure sudo group users are not 
# asked for a password when using 
# sudo command by ammending sudoers file
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN mkdir /src && chown -R developer:developer /src

USER developer
WORKDIR /src

RUN python3 -m venv py3venv \ 
    && . py3venv/bin/activate \
    && pip install -U pip \
    && pip install wheel build cmake

ENV VIRTUAL_ENV=/src/py3venv
ENV PYTHONPATH=cmakebuild/dev-unix/
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}
CMD exec /bin/bash

# To build:
# docker build . -t ubuntu2204-pytango-dev
# To run interactively:
# docker run -it --rm -v $(pwd):/src/pytango --name u22-pytango-dev ubuntu2204-pytango-dev
# To run a configure/build/other command...
# 