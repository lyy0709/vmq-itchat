# WEBHOOK.PY

import json
import os
import logging
import random
import string
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Union
import uvicorn
import itchat
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("webhook")

# 定义Pydantic模型
class MessageData(BaseModel):
    content: str

class MessageItem(BaseModel):
    to: str
    data: Union[MessageData, List[MessageData]]

class WebhookPayload(BaseModel):
    __root__: List[MessageItem]

# 初始化FastAPI
app = FastAPI()

# 加载或生成token
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_or_create_token():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    token = config.get('webhook_token')
    if not token:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        config['webhook_token'] = token
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        log.info(f"生成新的token: {token}")
    else:
        log.info(f"使用现有的token: {token}")
    return token

# 定义发送消息的函数
def send_msg(msg: str, toUserName: str):
    '''发送纯文本消息
    '''
    # 假设已经登录itchat
    itchat.send(msg=msg, toUserName=toUserName)
    log.info(f"发送消息给 {toUserName}: {msg}")
@app.post("/webhook/msg/v2")
async def webhook_endpoint(payload: WebhookPayload, token: str = Query(...)):
    if token != PERSONAL_TOKEN:
        log.warning("无效的token访问")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    for item in payload.__root__:
        to_user = item.to
        data = item.data
        if isinstance(data, list):
            for msg in data:
                send_msg(msg.content, to_user)
        else:
            send_msg(data.content, to_user)
    log.info("成功处理Webhook请求")
    return {"status": "success"}

def initialize(config):
    global PERSONAL_TOKEN
    PERSONAL_TOKEN = load_or_create_token(config)
    itchat.run()
    # 更新 PERSONAL_TOKEN in the app
    # Define a new event loop or update the existing one if necessary
    # 启动 FastAPI 服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)