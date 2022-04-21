# Docker images for documentation development

## Introduction

Docker containers are useful for developing PyTango locally.

## Building the Docker image

From within this folder, run commands like the following:

```shell script
docker build . -t pytango-doc
```

## Make documentation in a container

Run an instance of the container, volume mounting an external PyTango repo into the container.  For example:

```shell script
docker run -it --rm -v ~/tango-src/pytango:/opt/pytango pytango-doc /bin/bash
```

Inside the container:

go to /opt/pytango folder 
```shell script
cd /opt/pytango
```
and build the documentation 

```shell script
python -m sphinx doc build/sphinx
```

After building, open the [file:///<your-pytango-folder>/build/sphinx/index.html](file:///<your-pytango-folder>/build/sphinx/index.html) page in your browser.

## Using a container with an IDE

Once the image has been built, it can be used with IDEs like
[PyCharm](https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html#config-docker)
(Professional version only), and
[Visual Studio Code](https://code.visualstudio.com/docs/remote/containers)

### PyCharm

Add a new interpreter:

- Open the _Add Interpreter..._ dialog
- Select _Docker_
- Pick the image to use, e.g., `pytango-doc:latest`

Compile documentation:

- Make a new configuration
- Select "Module name" and type `sphinx`
- Enter parameters: `doc build/sphinx`

Now you can also debug the documentation creation...