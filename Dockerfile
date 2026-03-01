# 使用官方轻量级 Python 运行时作为父镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装必要的运行时系统依赖（减少镜像体积）
# libxml2 和 libxslt 是解析文档可能需要的库
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖清单并安装 Python 依赖
# 利用 Docker 缓存机制，只有 requirements.txt 变化时才重新执行 pip install
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有代码到容器的 /app 目录
COPY . .

# 创建应用需要的目录并设置权限
RUN mkdir -p uploads logs && chmod 755 uploads logs

# 微信云托管容器必须监听 80 端口
EXPOSE 80

# 设置环境变量
# 确保 Python 输出直接打印到日志，不进行缓冲
ENV PYTHONUNBUFFERED=1
# 默认环境设置为生产环境
ENV ENVIRONMENT=staging

# 添加健康检查（微信云托管会根据此状态判断服务是否正常）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# 启动命令：使用 uvicorn 运行 FastAPI 应用
# 注意：必须监听 0.0.0.0 和 80 端口
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]