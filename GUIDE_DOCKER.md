# 🐳 OpenRGD Docker Guide

The OpenRGD CLI is available as a Docker container, enabling zero-install usage and easy integration into CI/CD pipelines.

---

## 1. Quick Start

### Run the CLI directly
You can run any `rgd` command inside a container without installing Python.

```bash
# Build the image locally (if not pushed to Docker Hub yet)
docker build -t openrgd/cli .
```

# Verify installation
docker run --rm openrgd/cli --help
2. Working with Files (The Volume Trick)
Since Docker containers are isolated, running rgd init or rgd compile-spec inside a container won't save files to your host machine by default. You must use Volume Mounting.

Creating a New Robot (init)
To create a robot folder on your actual desktop/server:

Linux / macOS:

Bash

docker run --rm -v "$(pwd):/host" -w /host openrgd/cli init Jarvis
Windows (PowerShell):

PowerShell

docker run --rm -v "${PWD}:/host" -w /host openrgd/cli init Jarvis
Command Breakdown:

-v "$(pwd):/host": Maps your current folder to /host inside the container.

-w /host: Sets the working directory to that mapped folder.

openrgd/cli: The image name.

init Jarvis: The standard OpenRGD command.

Compiling & Exporting
To compile a spec inside an existing robot folder:

Bash

cd Jarvis
docker run --rm -v "$(pwd):/host" -w /host openrgd/cli compile-spec
3. CI/CD Integration (GitHub Actions / GitLab)
OpenRGD is designed for automated pipelines. Use the --quiet flag to keep logs clean.

Example: GitHub Action Step

YAML

steps:
  - name: Checkout Code
    uses: actions/checkout@v3

  - name: Compile Robot Spec
    uses: docker://openrgd/cli:latest
    with:
      args: compile-spec --output-base my_robot_spec

  - name: Verify Twins Integrity
    uses: docker://openrgd/cli:latest
    with:
      args: verify-twins my_robot_spec
4. Building the Image Manually
If you are modifying the CLI source code and want to test it in Docker:

Ensure the Dockerfile is in the project root.

Run the build command:

Bash

docker build -t openrgd/cli:dev .
Run your dev image:

Bash

docker run --rm openrgd/cli:dev check