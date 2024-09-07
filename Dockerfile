# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到工作目录
COPY . /app

# 安装所需的 Python 包
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用程序端口（如果有）
# EXPOSE 8000

# 运行应用程序
CMD ["python", "zfhd.py"]