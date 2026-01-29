# 阶段1：构建阶段
FROM debian:bookworm-slim AS builder

# 1. 安装构建工具
RUN apt update && apt install -y --no-install-recommends \
    wget curl unzip tar gcc libc6-dev libffi-dev libssl-dev \
    python3-dev python3-pip nodejs npm \
    && apt clean && rm -rf /var/lib/apt/lists/*

# 2. 安装 Python 依赖
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
COPY packages/brain/requirements.txt /builder/requirements.txt
# Debian 12 (Bookworm) 强制 PEP 668，需加 --break-system-packages
RUN pip3 install --no-cache-dir --upgrade pip --break-system-packages && \
    pip3 install --no-cache-dir -r /builder/requirements.txt --break-system-packages && \
    rm -rf /root/.cache/pip

# 3. 安装 code-server
RUN wget -qO- https://github.com/coder/code-server/releases/download/v4.20.0/code-server-4.20.0-linux-amd64.tar.gz | tar -xz -C /tmp \
    && mkdir -p /builder/code-server \
    && cp -r /tmp/code-server-4.20.0-linux-amd64/bin /builder/code-server/ \
    && cp -r /tmp/code-server-4.20.0-linux-amd64/lib /builder/code-server/ \
    && cp /tmp/code-server-4.20.0-linux-amd64/package.json /builder/code-server/ \
    && rm -rf /tmp/*

# 4. 准备配置和代码
COPY packages/brain/supervisord.conf /builder/config/supervisord.conf
COPY packages/brain /builder/brain
COPY packages/skills /builder/skills

# 阶段2：运行阶段
FROM debian:bookworm-slim AS runtime

# 1. 安装运行时系统依赖
RUN apt update && apt install -y --no-install-recommends \
    python3 python3-pip nodejs \
    git supervisor procps \
    chromium chromium-driver \
    libstdc++6 libx11-6 libxext6 libxrender1 fonts-dejavu \
    && apt clean && rm -rf /var/lib/apt/lists/*

# 2. 复制核心文件
# 注意：pip install 默认安装到 /usr/local/lib/python3.11/dist-packages (Debian)
COPY --from=builder /usr/local/lib/python3.11/dist-packages /usr/local/lib/python3.11/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /builder/code-server /opt/code-server
COPY --from=builder /builder/config/supervisord.conf /etc/supervisord.conf
COPY --from=builder /builder/brain /app/brain
COPY --from=builder /builder/skills /app/skills

# 3. 环境变量
ENV PATH="/opt/code-server/bin:${PATH}"
ENV CHROME_PATH="/usr/bin/chromium"
ENV PLAYWRIGHT_BROWSERS_PATH="0"
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH="/usr/bin/chromium"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

# 4. 暴露端口
EXPOSE 8080

# 5. 启动
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
