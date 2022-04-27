from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.adapters.onebot.v11.utils import escape
from nonebot import on_command
from nonebot.params import CommandArg

m = on_command("取码")


@m.handle()
async def get_cqcode(msg: Message = CommandArg()):
    await m.send(escape(str(msg)))
