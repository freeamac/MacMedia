# MacMedia
MacMedia Media Library Tracker

# Development

## Development Environment

A virtual environment should be set up with the imports defined in the *requirements.txt* file.

For running the application, Docker containers are used. Docker Desktop should be installed and
configured to use WSL 2. For example, in this case, the configuration is for Ubuntu:
![Configure WSL 2 Docker](app/docs/static/docker_wsl_config.png)

## Developer Testing

The application can be built into a docker image using the included `Dockerfile`. The image can be created
and launched using the `Makefile` targets:
```
    make build
    make run-dev
```
The running application in the Docker container can then be accessed at the url __http://localhost:5000/main__.


---

# Documentation

Sphinx and reStructuredText are utilized to create developer originated documentation.
The __.rst__ files are located under the `app/docs` directory. A top level `Makefile` is
used to generate the documentation with the command:
```
    make docs
```
The root of the resulting html documentation is `app/docs/_build/html/index.html`.
