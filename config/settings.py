import os
import yaml

ENV = os.getenv("ENV", "dev")  # 默认 dev

with open("config/envs.yaml", "r",encoding="utf-8") as f:
    ENVS = yaml.safe_load(f)

SETTINGS = ENVS[ENV]

"""
settings.py 是业务环境配置，playwright.config.py 是测试执行策略，两者分开管理。
"""
