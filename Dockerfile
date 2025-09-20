FROM python:slim

# Install Node.js and pnpm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy app directory with frontend files
COPY app /microblog/app

# Install frontend dependencies and build CSS
WORKDIR /microblog/app
RUN pnpm install --frozen-lockfile
RUN pnpm build

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

# Place executables in the environment at the front of the path
ENV FLASK_APP=microblog.py
ENV PATH="/microblog/.venv/bin:$PATH"

# Translate the application
RUN flask translate compile

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]