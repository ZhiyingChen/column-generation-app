FROM python:3.9-slim

WORKDIR /.

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    glpk-utils \
    && rm -rf /var/lib/apt/lists/*


# 然后复制所有代码（包括 app.py）
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 7860  # Hugging Face 默认监听 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

# 修改 ENTRYPOINT 的端口为 7860
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]