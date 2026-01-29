FROM docker.m.daocloud.io/python:3.12-slim

# Environment Variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Install System Dependencies
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install PM2 globally
RUN npm config set registry https://registry.npmmirror.com && \
    npm install pm2 -g

# Install Python Tools
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    pandas \
    playwright \
    fastapi \
    uvicorn \
    requests \
    beautifulsoup4 \
    duckduckgo-search \
    google-genai \
    langchain \
    langgraph

# Install Playwright Browsers
RUN playwright install chromium --with-deps

# Setup Workspace
WORKDIR /workspace
RUN mkdir -p /app/data && chmod 777 /app/data

# Install Brain Core SDK
COPY packages/brain/core /app/brain/core
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV BRAIN_DB_PATH="/app/data/brain.db"

# Entrypoint
CMD ["/bin/bash"]
