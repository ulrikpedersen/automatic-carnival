# Docker images for development

## Introduction

Docker containers are useful for developing PyTango locally.  This folder is for that purpose, and
the Docker images provide a similar environment to that used by Travis for the Continuous Integration
tests.  The name of the folder is chosen to match Visual Studio Code's naming convention.
Using some command line overrides, images for various versions of Python and Tango can be built.

## Building the Docker image

From within the pytango root folder, run commands like the following:

```shell script
docker build .devcontainer/ -t ubuntu2204-pytango-dev
```

Note: 
- the `--platform=linux/amd64 ` parameter is useful if not running on a linux/amd64 platform  
  (e.g., Apple Silicon) although this image does build natively on `--platform=linux/arm64`.

## Build, install and test PyTango in a container

Run an instance of the container, volume mounting an external PyTango repo into the container.  For example
(assuming PYTHON_VERSION and CPP_TANGO_VERSION are still set as above). From the root of the pytango module:

```shell script
docker run -it --rm -v $(pwd):/src/pytango --name u22-pytango-dev ubuntu2204-pytango-dev
```

Inside the container build and install the wheel:

```shell script
cd /src/pytango
python -m build
pip install dist/*.whl
```

Basic check that the build and install has worked:
```shell
cd /src   # Step out of the pytango root or you will not be able to import tango from the installed wheel
python -c "import tango; print(tango.utils.info())"
PyTango 9.4.0rc2 (9, 4, 0, 'rc', 2)
PyTango compiled with:
    Python : 3.10.6
    Numpy  : PYTANGO_NUMPY_VERSION
    Tango  : 9.4.0
    Boost  : 1.74.0

PyTango runtime is:
    Python : 3.10.6
    Numpy  : 1.24.1
    Tango  : 9.4.0

PyTango running on:
uname_result(system='Linux', node='548deafc4ec7', release='5.15.49-linuxkit', version='#1 SMP PREEMPT Tue Sep 13 07:51:32 UTC 2022', machine='aarch64')
```

Running the full unittest suite with pytest:
```shell
cd /src/pytango
pytest
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
- Pick the image to use, e.g., `ubuntu2204-pytango-dev`

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

Developing in a container from within VScode requires installation of the 
["Dev Containers" extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
(formerly known as - and still sometimes referred to - as "Remote Containers").

When opening the pytango folder in VScode, the Dev Containers extension will detect the presence of a `devcontainer.json` container configuration file, and will offer to reopen the folder in the container. The first time this is done, it will take a long time because the docker image must be built; after that first time, the image is cached.

Once in the container, your `pytango` folder will be mounted at `/workspaces/pytango`.

With VS Code in the Dev Container mode and opening a Terminal; you will find yourself in the pytango source dir, ready to build and test:

```shell script
python -m build
pip install dist/*.whl
pytest
```