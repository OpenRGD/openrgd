# 🐳 OpenRGD Docker Guide

Docker is an optional convenience for running the OpenRGD CLI in an isolated environment.

## Build locally

```bash
docker build -t openrgd/cli:dev .
docker run --rm openrgd/cli:dev --help
```

## Bring an example alive

Mount the repository so generated files remain on the host:

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -w /workspace \
  openrgd/cli:dev \
  alive example/minimal-arm/openrgd_minimal_arm.urdf
```

PowerShell:

```powershell
docker run --rm `
  -v "${PWD}:/workspace" `
  -w /workspace `
  openrgd/cli:dev `
  alive example/minimal-arm/openrgd_minimal_arm.urdf
```

## CI/CD

For CI, prefer deterministic/quiet output:

```bash
rgd --quiet check
```

The repository currently builds the Python/Windows toolchain in GitHub Actions. Docker images are not automatically published by the project at this time; `openrgd/cli:dev` in this guide is a locally built image name.
