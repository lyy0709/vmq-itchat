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
            - ${PWD}/config.json/:/app/config.json
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
| webhook_url|企业微信机器人通知链接 |
|paytype|qrcode或者reward（代表普通收款码和赞赏码）|

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
