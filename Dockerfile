FROM python:3.12-slim

WORKDIR /opt/openrgd

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip install --no-cache-dir .

WORKDIR /workspace
ENTRYPOINT ["rgd"]
CMD ["--help"]
