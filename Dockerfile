# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff5 \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    ttf-dejavu \
    fonts-noto-cjk \
    && apt-get clean

# 拷贝项目代码
COPY ./app /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预创建缓存目录
RUN mkdir -p /app/imgs /app/img_cache /app/fonts

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
