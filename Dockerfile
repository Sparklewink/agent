# 使用轻量的 Python 镜像
FROM python:3.9-slim

# 安装 curl 和 unzip 依赖
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 创建一个没有特权的普通用户
RUN useradd -ms /bin/bash appuser

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制主程序
COPY app.py .

# 将工作目录的所有权交给刚刚创建的普通用户
RUN chown -R appuser:appuser /app

# 切换到这个普通用户来运行程序
USER appuser

# 暴露 Koyeb 需要的端口
EXPOSE 8080

# **最终修正点**: 使用 Gunicorn 启动 Flask 应用，它会完美监听 Koyeb 指定的 $PORT 端口
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 app:app