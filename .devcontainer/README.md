# Docker images for development

## Introduction

Docker containers are useful for developing PyTango locally.  This folder is for that purpose, and
the Docker images provide a similar environment to that used by Travis for the Continuous Integration
tests.  The name of the folder is chosen to match Visual Studio Code's naming convention.
Using some command line overrides, images for various versions of Python and Tango can be built.

## Building the Docker image

From within this folder, run commands like the following:

```shell script
export PYTHON_VERSION=3.10
export CPP_TANGO_VERSION=9.4.0
docker build . --platform=linux/amd64 -t pytango-dev:py${PYTHON_VERSION}-tango${CPP_TANGO_VERSION} --build-arg PYTHON_VERSION --build-arg CPP_TANGO_VERSION
```

Note: 
- the cppTango version must exist on conda-forge:  https://anaconda.org/conda-forge/cpptango
- the `--platform=linux/amd64 ` parameter is useful if not running on a linux/amd64 platform  
  (e.g., Apple Silicon) - without the parameter conda may fail to find compatible packages.

## Build, install and test PyTango in a container

Run an instance of the container, volume mounting an external PyTango repo into the container.  For example:

```shell script
docker run -it --rm -v ~/tango-src/pytango:/opt/pytango pytango-dev:py3.10-tango9.4.0
```

Inside the container:

```shell script
cd /opt/pytango
python setup.py build
python setup.py test
```

## Using a container with an IDE

Once the image has been built, it can be used with IDEs like
[PyCharm](https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html#config-docker)
(Professional version only), and
[Visual Studio Code](https://code.visualstudio.com/docs/remote/containers)

### PyCharm

Add a new interpreter:

- Open the _Add Interpreter..._ dialog
- Select _Docker_
- Pick the image to use, e.g., `pytango-dev:py3.10-tango9.4.0`

Running tests:

- If you want to run all the tests, it will work out the box.
- If you only want to run a subset, the `setup.cfg` file needs to be change temporarily:
  - In the `[tool:pytest]` section, remove the `tests` path from the additional options, to give:
     `addopts = -v --forked`
  - If the change isn't made you may get errors like:

    ```
    collecting ... collected 0 items
    ERROR: file not found: tests
    ```

### Visual Studio Code

Developing in a container from within VScode requires installation of the "Remote Containers" extension.

When opening the pytango folder in VScode, the Remote Containers extension will detect the presence of a `devcontainer.json` container configuration file, and will offer to reopen the folder in the container. The first time this is done, it will take a long time because the docker image must be built; after that first time, the image is cached.

Once in the container, your `pytango` folder will be mounted at `/workspaces/pytango`.
