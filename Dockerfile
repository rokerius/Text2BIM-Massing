FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY . .
RUN python -m pip install --no-cache-dir '.[dev,llm,mesh,maslov]'
CMD ["python", "-m", "pytest", "-c", "pyproject.toml", "tests", "-q"]
