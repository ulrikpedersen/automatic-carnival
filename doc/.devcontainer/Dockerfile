# Simple docker file to create Docker with pre-installed packages to compile docs

FROM sphinxdoc/sphinx

# GCC may be required to compile psutil, depending on platform
RUN apt update && apt install -y gcc

RUN python -m pip install --upgrade pip && \
    python -m pip install numpy gevent psutil sphinx_rtd_theme