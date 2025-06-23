# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# System deps for psycopg2, etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m sweetuser

WORKDIR /app

# Builder stage: install dependencies in a venv
FROM base AS builder


# Use pip cache for faster builds
#RUN .venv/bin/pip install "Django==5.2.2"
#RUN .venv/bin/pip install "django-extensions==4.1"
#RUN .venv/bin/pip install "djangorestframework==3.16.0"
#RUN .venv/bin/pip install "inflection==0.5.1"
#RUN .venv/bin/pip install "uritemplate==4.2.0"
#RUN .venv/bin/pip install "pyyaml==6.0.2"
#RUN .venv/bin/pip install "pandas==2.3.0"
#RUN .venv/bin/pip install "openpyxl==3.1.5"
#RUN .venv/bin/pip install "dj-database-url==3.0.0"
#RUN .venv/bin/pip install "python-decouple==3.8"
#RUN .venv/bin/pip install "psycopg==3.2.9"



# Copy only requirements.txt first for better cache
COPY --link requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# Copy application code
COPY --link core/ ./core/
COPY --link manufature/ ./manufature/
COPY --link orders/ ./orders/
COPY --link products/ ./products/
COPY --link templates/ ./templates/
COPY --link manage.py ./manage.py
COPY --link docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod a+x /docker-entrypoint.sh

# Final stage: minimal image with venv and app code
FROM base AS final

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy app code from builder
COPY --from=builder /app/core /app/core
COPY --from=builder /app/manufature /app/manufature
COPY --from=builder /app/orders /app/orders
COPY --from=builder /app/products /app/products
COPY --from=builder /app/templates /app/templates
COPY --from=builder /app/manage.py /app/manage.py
COPY --from=builder /docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod a+x /docker-entrypoint.sh

# Set permissions for non-root user
RUN chown -R sweetuser:sweetuser /app

####################################


# Cria a pasta /static (se não existir) e ajusta permissões
RUN mkdir -p /static && \
    chown -R sweetuser:sweetuser /static && \
    chmod -R 755 /static


###################################
USER sweetuser

ENTRYPOINT ["/docker-entrypoint.sh"]




