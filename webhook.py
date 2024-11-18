# WEBHOOK.PY

import json
import os
import logging
import random
import string
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, RootModel
from typing import List, Union
import uvicorn
import itchat

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("webhook")

# 定义Pydantic模型
class MessageData(BaseModel):
    content: str

class MessageItem(BaseModel):
    to: str
    data: Union[MessageData, List[MessageData]]

class WebhookPayload(RootModel[List[MessageItem]]):
    pass

# 初始化FastAPI
app = FastAPI()

# 加载或生成token
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_or_create_token(config):
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

PERSONAL_TOKEN = ""  # 初始化为空，稍后在initialize中设置

# 定义发送消息的函数
def send_msg(msg: str, toUserName: str):
    '''发送纯文本消息'''
    try:
        itchat.send(msg=msg, toUserName=toUserName)
        log.info(f"发送消息给 {toUserName}: {msg}")
    except Exception as e:
        log.error(f"发送消息失败给 {toUserName}: {e}")

@app.post("/webhook/msg/v2")
async def webhook_endpoint(payload: WebhookPayload, token: str = Query(...)):
    if token != PERSONAL_TOKEN:
        log.warning("无效的token访问")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    for item in payload.model:
        to_user = item.to
        data = item.data
        if isinstance(data, list):
            for msg in data:
                send_msg(msg.content, to_user)
        else:
            send_msg(data.content, to_user)
    log.info("成功处理Webhook请求")
    return {"status": "success"}

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def initialize(config):
    global PERSONAL_TOKEN
    PERSONAL_TOKEN = load_or_create_token(config)
    # 启动 FastAPI 服务器
    run_server()