import asyncio

import re
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot import on_command
from nonebot.params import CommandArg

matcher = on_command("quit", aliases={"退群"})


@matcher.handle()
async def quit_group(bot: Bot, arg: Message = CommandArg()):
    args: str = arg.extract_plain_text().split()
    m: list = re.findall(r'^\d+$', args)
    if not m:
        return
    await asyncio.gather(*(bot.set_group_leave(group_id=int(gid)) for gid in m))
    msg = f'已尝试退出{len(m)}个群'
    # if failed:
    #     msg += f"\n失败{len(failed)}个群：{failed}"
    await matcher.send(msg)
