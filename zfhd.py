import hashlib
import requests
import time
import threading
import re
import os
import logging
import json
import xml.etree.ElementTree as ET
import itchat, time
from itchat.content import *

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取当前脚本所在目录
current_file_path = os.path.abspath(os.path.dirname(__file__))

# 构建相对路径
config_file_path = os.path.join(current_file_path, './config/config.json')

# 规范化路径
config_file_path = os.path.normpath(config_file_path)

# 加载配置
try:
    with open(config_file_path, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error("配置文件 'config.json' 未找到")
    raise

paytype = config.get('paytype', 'qrcode')
ssl = config.get('ssl', False)
if ssl:
    protocol = 'https'
else:
    protocol = 'http'

class WeChatPayMonitor:
    def __init__(self, host, key):
        self.host = host
        self.key = key

    def md5(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def app_push(self, amount):
        t = str(int(time.time() * 1000))
        sign = self.md5(f"1{amount}{t}{self.key}")
        url = f"{protocol}://{self.host}/appPush?t={t}&type=1&price={amount}&sign={sign}"
        try:
            response = requests.get(url)
            logger.info(f"Push response: {response.text}")
            response_json = response.json()
            if response_json.get('code') == 0:
                print(f"回调成功: 金额 {amount} 元")
                return True
            else:
                print(f"回调失败: {response_json.get('msg', '未知错误')}")
                return False
        except Exception as e:
            logger.error(f"Push failed: {e}")
            print(f"回调异常: {str(e)}")
            return False  
            
    def send_heartbeat(self):
        while True:
            t = str(int(time.time() * 1000))
            sign = self.md5(f"{t}{self.key}")
            url = f"{protocol}://{self.host}/appHeart?t={t}&sign={sign}"
            try:
                response = requests.get(url, timeout=10)  # 设置请求超时时间为10秒
                response.raise_for_status()  # 检查请求是否成功
                logger.info(f"Heartbeat response: {response.text}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Heartbeat failed: {e}")
                # 增加重试机制
                for i in range(3):  # 重试3次
                    try:
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        logger.info(f"Heartbeat response (retry {i+1}): {response.text}")
                        break
                    except requests.exceptions.RequestException as retry_e:
                        logger.error(f"Heartbeat retry {i+1} failed: {retry_e}")
                        time.sleep(5)  # 重试前等待5秒
            time.sleep(60)  # 每60秒发送一次心跳
            
    @staticmethod
    def extract_money_from_des(des):
        # 分割字符串并查找包含"收款金额"的行
        lines = des.split('\\n')
        for line in lines:
            if "收款金额" in line:
                match = re.search("￥(\\d+\\.\\d{2})", line)
                if match:
                    return match.group(1)
        logger.warning(f"Failed to extract money from des: {des}")
        return None
        
    def handle_message(self, msg):
        """
        处理所有微信消息，检查支付通知
        """
        is_payment = False  # 初始化 is_payment
        try:
            # 解析XML内容
            root = ET.fromstring(msg.content)
            appmsg = root.find('appmsg')
            
            if appmsg is not None:
                title = appmsg.find('title').text if appmsg.find('title') is not None else ''
                des = appmsg.find('des').text if appmsg.find('des') is not None else ''

                logger.info(f"Extracted title: '{title}'")
                logger.info(f"Extracted des: '{des}'")

                # 判断是否是二维码微信支付通知或赞赏码通知
                if paytype == 'qrcode':
                    is_payment = "微信支付收款" in title or "个人收款码到账" in title
                elif paytype == 'reward':
                    is_payment = "二维码赞赏到账" in title
                logger.info(f"Is this a payment message? {'Yes' if is_payment else 'No'}")

                if is_payment:
                    money = self.extract_money_from_des(des)
                    if money:
                        logger.info(f"WeChat payment received: {money} CNY")
                        callback_success = self.app_push(float(money))
                        if not callback_success:
                            print(f"回调失败，请检查网络或服务器状态")
                    else:
                        logger.warning("Failed to extract money from WeChat notification")
                        print("提取支付金额失败，请检查消息格式")
                else:
                    logger.debug("This is not a payment notification.")
            else:
                logger.warning("Failed to find 'appmsg' element in the XML")

        except ET.ParseError as e:
            logger.exception(f"Error parsing XML: {e}")
            print(f"解析XML时发生错误: {str(e)}")
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            print(f"处理消息时发生错误: {str(e)}")

        # 在每条消息处理后输出判断结果
        print(f"Is this a payment message? {'Yes' if is_payment else 'No'}")
        
def initialize(config):
    monitor = WeChatPayMonitor(host=config.get('host'), key=config.get('key'))

    @itchat.msg_register(SHARING, isMpChat=True)
    def text_reply(msg):
        """
        处理所有微信消息事件。
        """
        logger.info("微信消息监控")
        monitor.handle_message(msg)

    logger.info("启动 heartbeat 线程。")
    heartbeat_thread = threading.Thread(target=monitor.send_heartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()
    itchat.run()
    logger.info("开始运行 itchat。")