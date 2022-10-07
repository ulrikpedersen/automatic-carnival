# Source for base image:  https://github.com/conda-forge/docker-images

FROM condaforge/mambaforge:4.14.0-0

ARG PYTHON_VERSION=3.10
ARG CPP_TANGO_VERSION=9.4.0
ARG TANGO_TEST_VERSION=3.6

# setting default shell to bash
SHELL ["/bin/bash", "--login", "-c"]

# install required packages
# - if we use cpptango dev - we have to build TangoTest, so also packages to build
RUN if [[ "${CPP_TANGO_VERSION}" = *"dev"* ]] || [[ "${CPP_TANGO_VERSION}" = *"rc"* ]]; then \
      export BUILD_DEPENDENCIES="build-essential cmake git libcos4-dev libomniorb4-dev libomnithread4-dev libzmq3-dev omniidl"; \
    fi && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install make pkg-config rsync $BUILD_DEPENDENCIES && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# setup conda environment
RUN mamba create --yes --name py$PYTHON_VERSION-tango$CPP_TANGO_VERSION python=$PYTHON_VERSION

# add conda environment to PATH
ENV PATH /opt/conda/envs/py"$PYTHON_VERSION"-tango"$CPP_TANGO_VERSION"/bin:$PATH

# setup environment to activate automatically, with correct vars
RUN mamba init bash && \
    echo "mamba activate py$PYTHON_VERSION-tango$CPP_TANGO_VERSION" >> ~/.bashrc && \
    echo "export CONDA_ENV_NAME=py$PYTHON_VERSION-tango$CPP_TANGO_VERSION" >> ~/.bashrc && \
    echo "export BOOST_ROOT=\$CONDA_PREFIX TANGO_ROOT=\$CONDA_PREFIX ZMQ_ROOT=\$CONDA_PREFIX OMNI_ROOT=\$CONDA_PREFIX" >> ~/.bashrc && \
    echo "export PYTHON_VERSION=$PYTHON_VERSION" >> ~/.bashrc && \
    echo "export BOOST_PYTHON_LIB=boost_python\${PYTHON_VERSION//./}" >> ~/.bashrc && \
    sed -i 's/\[ -z "\$PS1" \] && return/# disabled early exit for non-interactive usage in container!/' ~/.bashrc

# create conda environment in one step
# - install cpptango and PyTango extension build requirements
# - depending on Python we need different test utilities
# - depending on cppTango version, we may get TangoTest from conda-forge, or build from source
RUN if [[ "${PYTHON_VERSION}" = "2."* ]]; then \
      export PYTHON_TEST_PACKAGES="trollius futures 'pyparsing<3' 'pytest<5' 'pytest-xdist<2' 'gevent!=1.5a1' psutil enum34"; \
    else \
      export PYTHON_TEST_PACKAGES="pytest pytest-xdist 'gevent!=1.5a1' psutil"; \
    fi && \
    if [[ "${CPP_TANGO_VERSION}" = *"dev"* ]] || [[ "${CPP_TANGO_VERSION}" = *"rc"* ]]; then \
      export TANGO_TEST_PACKAGE=""; \
    else \
      export TANGO_TEST_PACKAGE=tango-test=$TANGO_TEST_VERSION; \
    fi && \
    mamba install --yes -c conda-forge -c tango-controls/label/dev -c conda-forge/label/cpptango_rc \
      boost cppzmq cxx-compiler numpy six cpptango=$CPP_TANGO_VERSION $TANGO_TEST_PACKAGE $PYTHON_TEST_PACKAGES && \
    mamba clean --all --force-pkgs-dirs --yes

# if we use cpptango dev/rc - we build TangoTest
RUN if [[ "${CPP_TANGO_VERSION}" = *"dev"* ]] || [[ "${CPP_TANGO_VERSION}" = *"rc"* ]]; then \
      git clone --depth 1 -b "$TANGO_TEST_VERSION" https://gitlab.com/tango-controls/TangoTest.git /tangotest && \
      cmake -B /tangotest/build -DCMAKE_CXX_COMPILER=/usr/bin/x86_64-linux-gnu-g++ -DTANGO_WARNINGS_AS_ERRORS=ON /tangotest && \
      make -C /tangotest/build install; \
    fi
