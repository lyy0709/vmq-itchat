# APP.PY

import json
import os
import logging
import threading
import sys
from fastapi import FastAPI
import uvicorn
import itchat

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if not os.path.exists(config_path):
        log.error("config.json 文件不存在。")
        sys.exit(1)
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_zfhd(config):
    import zfhd
    zfhd.initialize(config)

def run_webhook(config):
    import webhook
    webhook.initialize(config)

def main():
    config = load_config()
    models = config.get('models', [])

    if not models:
        log.error("配置文件中未指定任何模型。")
        sys.exit(1)

    # 登录 WeChat (itchat)
    log.info("启动 wechat 登录。请扫描二维码登录...")
    itchat.auto_login(True)
    log.info("微信登录成功。")

    threads = []

    if 'zfhd' in models or 'all' in models:
        log.info("启动 zfhd 模块。")
        t_zfhd = threading.Thread(target=run_zfhd, args=(config,))
        t_zfhd.start()
        threads.append(t_zfhd)

    if 'webhook' in models or 'all' in models:
        log.info("启动 webhook 模块。")
        t_webhook = threading.Thread(target=run_webhook, args=(config,))
        t_webhook.start()
        threads.append(t_webhook)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()