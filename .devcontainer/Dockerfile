FROM continuumio/miniconda3:4.9.2

ARG PYTHON_VERSION=3.7
ARG CPP_TANGO_VERSION=9.4.0dev0

# setting default shell to bash
SHELL ["/bin/bash", "--login", "-c"]

# install required packages
RUN apt-get update -y --allow-releaseinfo-change-suite; \
    apt-get -y install make pkg-config rsync

# if we use cpptango dev - we have to build TangoTest, so also packages to build
RUN if [[ "${CPP_TANGO_VERSION}" = *"dev"* ]]; then \
      apt-get -y install build-essential cmake git libcos4-dev libomniorb4-dev libomnithread4-dev libzmq3-dev omniidl; \
    fi

# setup conda environment
RUN conda update -n base -c defaults conda; \
    conda create --name py"$PYTHON_VERSION"-tango"$CPP_TANGO_VERSION" python="$PYTHON_VERSION"

# add conda environment to PATH
ENV PATH /opt/conda/envs/py"$PYTHON_VERSION"-tango"$CPP_TANGO_VERSION"/bin:$PATH

# setup the envs
RUN conda init bash; \
    echo "conda activate py$PYTHON_VERSION-tango$CPP_TANGO_VERSION" >> ~/.bashrc; \
    echo "export CONDA_ENV_NAME=py$PYTHON_VERSION-tango$CPP_TANGO_VERSION" >> ~/.bashrc; \
    echo "export BOOST_ROOT=\$CONDA_PREFIX TANGO_ROOT=\$CONDA_PREFIX ZMQ_ROOT=\$CONDA_PREFIX OMNI_ROOT=\$CONDA_PREFIX" >> ~/.bashrc; \
    echo "export PYTHON_VERSION=$PYTHON_VERSION" >> ~/.bashrc; \
    echo "export BOOST_PYTHON_LIB=boost_python\${PYTHON_VERSION//./}" >> ~/.bashrc

# install cpptango and main requirements to conda
RUN conda install --yes -c conda-forge -c defaults boost gxx_linux-64 cppzmq numpy; \
    conda install -c tango-controls/label/dev -c tango-controls -c conda-forge -c defaults cpptango=="$CPP_TANGO_VERSION"

# depending on Python we install different test utilities
RUN if [[ "${PYTHON_VERSION}" = "2."* ]]; then \
      conda install --yes -c conda-forge -c defaults trollius futures 'pyparsing < 3' 'pytest < 5' 'pytest-xdist < 2' 'gevent != 1.5a1' psutil enum34; \
    else \
      conda install --yes -c conda-forge -c defaults pytest pytest-xdist 'gevent != 1.5a1' psutil; \
    fi

# if we use cpptango dev - we have to build TangoTest
RUN if [[ "${CPP_TANGO_VERSION}" = *"dev"* ]]; then \
      git clone --depth 1 https://gitlab.com/tango-controls/TangoTest.git /tangotest && \
      cmake -B /tangotest/build -DCMAKE_CXX_COMPILER=/usr/bin/x86_64-linux-gnu-g++ -DTANGO_WARNINGS_AS_ERRORS=ON /tangotest && \
      make -C /tangotest/build install; \
# else just install it
    else \
        conda install -c tango-controls/label/dev -c tango-controls -c conda-forge -c defaults tango-test; \
    fi

# clean up
RUN apt-get autoremove -y; \
    apt-get clean -y; \
    rm -rf /var/lib/apt/lists/*

