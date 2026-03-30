# 使用 Playwright 官方镜像（已内置 Chromium + 所有系统依赖）
# 对应 requirements.txt 中的 playwright==1.48.0
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# 设置工作目录
WORKDIR /app

# 先只复制依赖文件（利用 Docker 层缓存：依赖不变就不重新安装）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制项目代码
COPY . .

# 默认命令：运行测试（headless 模式，slowmo=0）
CMD ["pytest", "--headless", "--slowmo", "0", "-v"]
