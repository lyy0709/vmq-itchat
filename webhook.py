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

# 定义 Pydantic 模型
class MessageData(BaseModel):
    content: str

class MessageItem(BaseModel):
    isRoom: bool = False
    to: str
    data: Union[MessageData, List[MessageData]]

class WebhookPayload(RootModel[List[MessageItem]]):
    pass

# 初始化 FastAPI
app = FastAPI()

current_file_path = os.path.abspath(os.path.dirname(__file__))

# 构建相对路径
config_file_path = os.path.join(current_file_path, './config/config.json')

# 规范化路径
config_file_path = os.path.normpath(config_file_path)

def load_or_create_token(config):
    token = config.get('webhook_token')
    if not token:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        config['webhook_token'] = token
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        log.info(f"生成新的 token: {token}")
    else:
        log.info(f"使用现有的 token: {token}")
    return token

PERSONAL_TOKEN = ""  # 初始化为空，稍后在 initialize 中设置

@app.post("/webhook/msg/v2")
async def webhook_endpoint(payload: WebhookPayload, token: str = Query(...)):
    if token != PERSONAL_TOKEN:
        log.warning("无效的 token 访问")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    for item in payload.root:  # 使用 payload.root 访问数据
        isroom = item.isRoom
        if isroom:
            to_room = item.to
            data = item.data
            if isinstance(data, list):
                for msg in data:
                    itchat.search_chatrooms(name=to_room)[0].send(msg.content)
            else:
                itchat.search_chatrooms(name=to_room)[0].send(data.content)
        else:
            to_user = item.to
            data = item.data
            if isinstance(data, list):
                for msg in data:
                    itchat.search_friends(nickName=to_user)[0].send(msg.content) 
            else:
                itchat.search_friends(nickName=to_user)[0].send(data.content)
    log.info("成功处理 Webhook 请求")
    return {"status": "success"}

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def initialize(config):
    global PERSONAL_TOKEN
    PERSONAL_TOKEN = load_or_create_token(config)
    # 启动 FastAPI 服务器
    run_server()