# argus/services/llm_parser/Dockerfile

# =================================================================
# Stage 1: Base - The common foundation
# =================================================================
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PATH="/usr/local/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# =================================================================
# Stage 2: Common Builder - Installs OS-level build tools
# Both prod and dev builders will use this as their base
# =================================================================
FROM base AS common-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# =================================================================
# Stage 3: Production Builder - Installs ONLY production dependencies
# =================================================================
FROM common-builder AS prod-builder

COPY services/llm_parser/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# =================================================================
# Stage 4: Development Builder - Installs ALL dependencies
# This builds ON TOP of the prod-builder for efficiency
# =================================================================
FROM prod-builder AS dev-builder

COPY services/llm_parser/requirements-dev.txt ./
COPY pyproject.toml ./
# This installs *only* the extra dev packages, since prod ones are inherited
RUN pip install --no-cache-dir -r requirements-dev.txt

# =================================================================
# Stage 5: Development - For local development with live-reload
# =================================================================
FROM dev-builder AS development

# Copy the entire project context
COPY services/llm_parser/ .
# This command still works, as dev-builder has debugpy
CMD ["python", "-Xfrozen_modules=off", "-m", "debugpy", "--listen", "0.0.0.0:5679", "--wait-for-client", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]

# =================================================================
# Stage 6: Production - A lean image for deployment
# =================================================================
FROM base AS production

# Copy only the lean production packages from the prod-builder
COPY --from=prod-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=prod-builder /usr/local/bin /usr/local/bin

# Copy the app directory to /app/app to match the import path
COPY services/llm_parser/app /app/app
COPY services/llm_parser/config /app/config
COPY services/llm_parser/data /app/data

# Expose the port the app runs on
EXPOSE 8002

# Command to run the app in production
CMD uvicorn app.main:app --host ${SERVICE__HOST:-0.0.0.0} --port ${SERVICE__PORT:-8002} --log-level ${SERVICE__LOG_LEVEL:-info}
