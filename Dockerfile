# Lets name this image: ubuntu2204-pytango-dev
FROM ubuntu:22.04
RUN apt-get update -q && \
    apt-get install -y -q sudo \
    build-essential git pkg-config gdb libtool autoconf automake \
    ca-certificates curl vim \
    python3 python3-pip python3-venv \
    lcov doxygen clang-tidy-12 cppcheck \
    libboost-python-dev libzmq3-dev libomniorb4-dev omniorb-idl libcos4-dev omniidl \
    unattended-upgrades
RUN unattended-upgrade
RUN apt-get purge unattended-upgrades -y
RUN pip3 install cmake
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

# build and install tangoidl
RUN git clone --depth 1 https://gitlab.com/tango-controls/tango-idl.git && \
    mkdir -p tango-idl/build && cd tango-idl && \
    cmake -S . -B build -DCMAKE_INSTALL_PREFIX=/usr/local/ && \
    cmake --build build && \
    sudo cmake --install build

# build and install cppTango
# cppTango 9.3.5 will attempt to build jpeg with MMX optimisations. This fails
# on CPU architectures that don't have that feature - i.e. docker --platform=linux/aarch64
# so we switch that off with the TANGO_JPEG_MMX option. 
# cppTango >= 9.4 have removed JPEG_MMX AND this cmake flag.
WORKDIR /src
RUN git clone https://gitlab.com/tango-controls/cppTango.git && \
    cd cppTango && git checkout 9.3.5 && \
    mkdir -p build && \
    cmake -S . -B build -DBUILD_TESTING=OFF -DIDL_BASE=/usr/local -DTANGO_JPEG_MMX=OFF && \
    cmake --build build && \
    sudo cmake --install build && \
    sudo ldconfig

WORKDIR /src
RUN python3 -m venv py3venv \ 
    && . py3venv/bin/activate \
    && pip install -U pip \
    && pip install wheel build cmake numpy

WORKDIR /src
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