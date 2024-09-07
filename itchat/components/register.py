import logging
import sys
import threading
import traceback
from functools import wraps

try:
    import Queue
except ImportError:
    import queue as Queue

from ..utils import test_connect
from ..storage import templates

logger = logging.getLogger('itchat')


def load_register(core):
    core.auto_login = auto_login
    core.configured_reply = configured_reply
    core.msg_register = msg_register
    core.command = command
    core.run = run


def auto_login(self, hotReload=False, statusStorageDir='itchat.pkl', loginCallback=None, exitCallback=None):
    if not test_connect():
        logger.info("You can't get access to internet or wechat domain, so exit.")
        sys.exit()
    self.useHotReload = hotReload
    self.hotReloadDir = statusStorageDir
    if hotReload:
        if self.load_login_status(statusStorageDir, loginCallback=loginCallback, exitCallback=exitCallback):
            return
        self.login(loginCallback=loginCallback, exitCallback=exitCallback)
        self.dump_login_status(statusStorageDir)
    else:
        self.login(loginCallback=loginCallback, exitCallback=exitCallback)


def configured_reply(self):
    ''' determine the type of message and reply if its method is defined
        however, I use a strange way to determine whether a msg is from massive platform
        I haven't found a better solution here
        The main problem I'm worrying about is the mismatching of new friends added on phone
        If you have any good idea, pleeeease report an issue. I will be more than grateful.
    '''
    try:
        msg = self.msgList.get(timeout=1)
    except Queue.Empty:
        pass
    else:
        if msg.get('Content') is not None and msg['Content'].startswith('/'):
            command_name = msg['Content'].split(' ')[0]
            func = None
            if command_name in self.command_functions['friend'].keys() and isinstance(msg['User'], templates.User):
                func = self.command_functions['friend'][command_name]
            elif command_name in self.command_functions['group'].keys() and isinstance(msg['User'], templates.Chatroom):
                func = self.command_functions['group'][command_name]
            if func is not None:
                try:
                    resp = func(msg['Content'], msg['User'])
                    if resp is not None:
                        self.send(resp, msg.get('FromUserName'))
                except ValueError as e:
                    self.send(str(e), msg.get('FromUserName'))
        else:
            if isinstance(msg['User'], templates.User):
                replyFn = self.functionDict['FriendChat'].get(msg['Type'])
            elif isinstance(msg['User'], templates.MassivePlatform):
                replyFn = self.functionDict['MpChat'].get(msg['Type'])
            elif isinstance(msg['User'], templates.Chatroom):
                replyFn = self.functionDict['GroupChat'].get(msg['Type'])
            if replyFn is None:
                r = None
            else:
                try:
                    r = replyFn(msg)
                    if r is not None:
                        self.send(r, msg.get('FromUserName'))
                except:
                    logger.warning(traceback.format_exc())


def msg_register(self, msgType, isFriendChat=False, isGroupChat=False, isMpChat=False):
    ''' a decorator constructor
        return a specific decorator based on information given '''
    if not (isinstance(msgType, list) or isinstance(msgType, tuple)):
        msgType = [msgType]

    def _msg_register(fn):
        for _msgType in msgType:
            if isFriendChat:
                self.functionDict['FriendChat'][_msgType] = fn
            if isGroupChat:
                self.functionDict['GroupChat'][_msgType] = fn
            if isMpChat:
                self.functionDict['MpChat'][_msgType] = fn
            if not any((isFriendChat, isGroupChat, isMpChat)):
                self.functionDict['FriendChat'][_msgType] = fn
        return fn

    return _msg_register


def command(self, name: str, detail: str, friend: bool = False,
            group: bool = False):
    def decorator(func):

        @wraps(func)
        def wrapper(message: str, *args, **kwargs):
            if message.startswith(name):
                if message[len(name):].strip() == "help":
                    raise ValueError(f"{detail}")
                # 截断命令名，只传递剩余的消息部分给函数
                return func(message[len(name):].strip().split(" "), *args, **kwargs)
            else:
                # 如果消息不是以命令名开始，可以抛出异常或返回特定值
                raise ValueError(f"Message does not start with the command name '{name}'")

        # 保存命令名作为函数的一个属性
        setattr(wrapper, 'command_name', name)
        # 好友回复
        if friend:
            self.command_functions['friend'][name] = wrapper
        # 群组回复
        if group:
            self.command_functions['group'][name] = wrapper
        return wrapper

    return decorator


def run(self, debug=False, blockThread=True):
    logger.info('Start auto replying.')
    if debug:
        logger.setLevel(level=logging.DEBUG)

    def reply_fn():
        try:
            while self.alive:
                self.configured_reply()
        except KeyboardInterrupt:
            if self.useHotReload:
                self.dump_login_status()
            self.alive = False
            logger.debug('itchat received an ^C and exit.')
            logger.info('Bye~')

    if blockThread:
        reply_fn()
    else:
        replyThread = threading.Thread(target=reply_fn)
        replyThread.setDaemon(True)
        replyThread.start()
