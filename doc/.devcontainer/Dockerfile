# Simple docker file to create Docker with pre-installed packadges to compile docs
# Y.Matveev, Marсh, 2022

FROM sphinxdoc/sphinx

RUN python -m pip install --upgrade pip
RUN python -m pip install six numpy
RUN python -m pip install sphinx_rtd_theme