# **vmq-itchat**

- vmq-itchat是基于itchat-uos编写的适用于vmq的微信监控，可以较长时间进行微信监控，使用linux即可部署

> 注意！！！
> - 使用该项目微信账号有被封禁的风险，请使用小号登陆。
> - 建议不要给太多人高频率使用，可能会导致账号被封禁。

## 部署

### Docker(不推荐)

```shell
docker run -d --name vmq-itchat \
-v ${PWD}/config.json:/app/config:json 
lyy0709/vmq-itchat:latest
```

### docker-compose(推荐）

```yaml
version: '3.9'
services:
    vmq-itchat:
        image: lyy0709/vmq-itchat:latest
        container_name: vmq-itchat
        volumes:
            - ${PWD}/config.json:/app/config.json
        restart: unless-stopped
```

### 登陆微信

查看`vmq-itchat`的日志

`docker logs vmq-itchat --tail 200 -f`或`docker compose logs vmq-itchat`（需要到部署文件夹）

扫码登陆即可。

> 注意！！！
> - 无法登陆的情况建议给小号绑上银行卡再试。

## config.json配置


| 变量 | 需填写的值 |
| ------- | ------- |
| host    |V免签域名地址（不带http或者https）|
| key|V免签回调key |
|paytype|qrcode或者reward（代表普通收款码和赞赏码）|
|ssl|true（选填，默认为false）true代表启用https|
|zzmzf|(选填，默认为false)true代表对接至尊码支付 （我自己测试无法匹配账单，待解决） |
|pid|（选填）当打开zzmzf后选择对接的通道  |

### 通知相关

- 更新采用青龙面板里的通知选择，具体如下，选择适合自己的填入config.json中即可，注意采用大写
```
    'HITOKOTO': "false",                  # 启用一言（随机句子）

    'BARK_PUSH': '',                    # bark IP 或设备码，例：https://api.day.app/DxHcxxxxxRxxxxxxcm/
    'BARK_ARCHIVE': '',                 # bark 推送是否存档
    'BARK_GROUP': '',                   # bark 推送分组
    'BARK_SOUND': '',                   # bark 推送声音
    'BARK_ICON': '',                    # bark 推送图标
    'BARK_LEVEL': '',                   # bark 推送时效性
    'BARK_URL': '',                     # bark 推送跳转URL

    'CONSOLE': False,                    # 控制台输出

    'DD_BOT_SECRET': '',                # 钉钉机器人的 DD_BOT_SECRET
    'DD_BOT_TOKEN': '',                 # 钉钉机器人的 DD_BOT_TOKEN

    'FSKEY': '',                        # 飞书机器人的 FSKEY

    'GOBOT_URL': '',                    # go-cqhttp
                                        # 推送到个人QQ：http://127.0.0.1/send_private_msg
                                        # 群：http://127.0.0.1/send_group_msg
    'GOBOT_QQ': '',                     # go-cqhttp 的推送群或用户
                                        # GOBOT_URL 设置 /send_private_msg 时填入 user_id=个人QQ
                                        #               /send_group_msg   时填入 group_id=QQ群
    'GOBOT_TOKEN': '',                  # go-cqhttp 的 access_token

    'GOTIFY_URL': '',                   # gotify地址,如https://push.example.de:8080
    'GOTIFY_TOKEN': '',                 # gotify的消息应用token
    'GOTIFY_PRIORITY': 0,               # 推送消息优先级,默认为0

    'IGOT_PUSH_KEY': '',                # iGot 聚合推送的 IGOT_PUSH_KEY

    'PUSH_KEY': '',                     # server 酱的 PUSH_KEY，兼容旧版与 Turbo 版

    'DEER_KEY': '',                     # PushDeer 的 PUSHDEER_KEY
    'DEER_URL': '',                     # PushDeer 的 PUSHDEER_URL

    'CHAT_URL': '',                     # synology chat url
    'CHAT_TOKEN': '',                   # synology chat token

    'PUSH_PLUS_TOKEN': '',              # push+ 微信推送的用户令牌
    'PUSH_PLUS_USER': '',               # push+ 微信推送的群组编码

    'WE_PLUS_BOT_TOKEN': '',            # 微加机器人的用户令牌
    'WE_PLUS_BOT_RECEIVER': '',         # 微加机器人的消息接收者
    'WE_PLUS_BOT_VERSION': 'pro',          # 微加机器人的调用版本

    'QMSG_KEY': '',                     # qmsg 酱的 QMSG_KEY
    'QMSG_TYPE': '',                    # qmsg 酱的 QMSG_TYPE

    'QYWX_ORIGIN': '',                  # 企业微信代理地址

    'QYWX_AM': '',                      # 企业微信应用

    'QYWX_KEY': '',                     # 企业微信机器人

    'TG_BOT_TOKEN': '',                 # tg 机器人的 TG_BOT_TOKEN，例：1407203283:AAG9rt-6RDaaX0HBLZQq0laNOh898iFYaRQ
    'TG_USER_ID': '',                   # tg 机器人的 TG_USER_ID，例：1434078534
    'TG_API_HOST': '',                  # tg 代理 api
    'TG_PROXY_AUTH': '',                # tg 代理认证参数
    'TG_PROXY_HOST': '',                # tg 机器人的 TG_PROXY_HOST
    'TG_PROXY_PORT': '',                # tg 机器人的 TG_PROXY_PORT

    'AIBOTK_KEY': '',                   # 智能微秘书 个人中心的apikey 文档地址：http://wechat.aibotk.com/docs/about
    'AIBOTK_TYPE': '',                  # 智能微秘书 发送目标 room 或 contact
    'AIBOTK_NAME': '',                  # 智能微秘书  发送群名 或者好友昵称和type要对应好

    'SMTP_SERVER': '',                  # SMTP 发送邮件服务器，形如 smtp.exmail.qq.com:465
    'SMTP_SSL': 'false',                # SMTP 发送邮件服务器是否使用 SSL，填写 true 或 false
    'SMTP_EMAIL': '',                   # SMTP 收发件邮箱，通知将会由自己发给自己
    'SMTP_PASSWORD': '',                # SMTP 登录密码，也可能为特殊口令，视具体邮件服务商说明而定
    'SMTP_NAME': '',                    # SMTP 收发件人姓名，可随意填写

    'PUSHME_KEY': '',                   # PushMe 的 PUSHME_KEY
    'PUSHME_URL': '',                   # PushMe 的 PUSHME_URL

    'CHRONOCAT_QQ': '',                 # qq号
    'CHRONOCAT_TOKEN': '',              # CHRONOCAT 的token
    'CHRONOCAT_URL': '',                # CHRONOCAT的url地址

    'WEBHOOK_URL': '',                  # 自定义通知 请求地址
    'WEBHOOK_BODY': '',                 # 自定义通知 请求体
    'WEBHOOK_HEADERS': '',              # 自定义通知 请求头
    'WEBHOOK_METHOD': '',               # 自定义通知 请求方法
    'WEBHOOK_CONTENT_TYPE': ''          # 自定义通知 content-type
```

## 相关项目

- https://github.com/littlecodersh/ItChat
- https://github.com/why2lyj/ItChat-UOS
- https://github.com/devcxl/WeChatBot

## 免责声明

- 本工具仅供学习和技术研究使用，不得用于任何商业或非法行为，否则后果自负。
- 本工具的作者不对本工具的安全性、完整性、可靠性、有效性、正确性或适用性做任何明示或暗示的保证，也不对本工具的使用或滥用造成的任何直接或间接的损失、责任、索赔、要求或诉讼承担任何责任。
- 本工具的作者保留随时修改、更新、删除或终止本工具的权利，无需事先通知或承担任何义务。
- 本工具的使用者应遵守相关法律法规，尊重微信的版权和隐私，不得侵犯微信或其他第三方的合法权益，不得从事任何违法或不道德的行为。
- 本工具的使用者在下载、安装、运行或使用本工具时，即表示已阅读并同意本免责声明。如有异议，请立即停止使用本工具，并删除所有相关文件。
