# Simple docker file to create Docker with pre-installed packages to compile docs

FROM sphinxdoc/sphinx

RUN python -m pip install --upgrade pip
RUN python -m pip install six numpy
RUN python -m pip install sphinx_rtd_theme