# 使用Python官方镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt到工作目录
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 复制应用代码到工作目录
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口80
EXPOSE 80

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]