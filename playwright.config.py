import os
from playwright.sync_api import Playwright

# 管理playwright 运行行为 -- node.js 才生效，pytest不生效

# 读取环境变量
ENV = os.getenv("ENV", "dev")  # 默认 dev

CONFIG = {
    "headless": True,
    "viewport": {"width": 1280, "height": 720},
    "screenshot": "only-on-failure", # 失败那一刻自动截图
    "video": "retain-on-failure", # 失败才留视频
    "trace": "retain-on-failure",  # 用例失败 → 保留 trace.zip ；用例成功 → 自动删除（不污染）
    "base_url": {
        "dev": "http://127.0.0.1:8000/",
        "staging": "http://127.0.0.1:8000/",
        "prod": "http://127.0.0.1:8000/"
    }[ENV]
}