FROM python:3.9-slim

ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_HEADLESS=true
ENV MPLCONFIGDIR=/tmp/mplcache

WORKDIR /app

# 👇 你必须确保 /tmp 是存在的（不能被误删或 copy 覆盖）
RUN mkdir -p /tmp /tmp/mplcache && chmod -R 777 /tmp

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    glpk-utils \
    && rm -rf /var/lib/apt/lists/*


# 然后复制所有代码（包括 app.py）
COPY . /app

RUN pip3 install -r requirements.txt

# Hugging Face 默认监听 7860
EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

# 修改 ENTRYPOINT 的端口为 7860
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]