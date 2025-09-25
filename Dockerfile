FROM python:slim

# Install Node.js and pnpm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    corepack enable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables that pnpm needs to function
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

# Copy app directory with frontend files
COPY app /microblog/app

# Install frontend dependencies and build CSS
WORKDIR /microblog/app
RUN pnpm install --frozen-lockfile
RUN pnpm build

# Install terser globally for JavaScript minification
RUN pnpm add -g terser

# Minify all JavaScript files in app/static/js (preserving original names)
RUN if [ -d "static/js" ]; then \
    for file in static/js/*.js; do \
        if [ -f "$file" ]; then \
            terser "$file" --compress --mangle -o "$file"; \
        fi \
    done \
    fi

# Copy preline.js to a permanent location before removing node_modules
RUN mkdir -p static/vendor && \
    cp node_modules/preline/dist/preline.js static/vendor/preline.js

# Clean up node_modules and package files as they're no longer needed
RUN rm -rf node_modules package.json pnpm-lock.yaml

# Remove terser
RUN pnpm remove -g terser

# Go back to root directory
WORKDIR /

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Return to the microblog directory
WORKDIR /microblog

# Copy uv project files
COPY pyproject.toml uv.lock ./

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Add server dependencies last
RUN uv add gunicorn

# Make boot script executable
RUN chmod a+x boot.sh

# Basic environment variables that the app needs to function correctly.
ENV FLASK_APP=microblog.py
ENV PRELINE_JS_DIR=static/vendor

# Place executables in the environment at the front of the path
# (so the Python environment doesn't need to be activated).
ENV PATH="/microblog/.venv/bin:$PATH"

# Translate the application
RUN flask translate compile

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]