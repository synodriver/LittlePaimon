import asyncio

import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot
from nonebot.exception import ActionFailed
from nonebot import on_command
from nonebot.params import CommandArg

matcher = on_command(('bc', '广播'))


@matcher.handle()
async def broadcast(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    su = event.user_id
    # for sid in hoshino.get_self_ids():  # fixme
    #     gl = await bot.get_group_list(self_id=sid)
    #     gl = [g['group_id'] for g in gl]
    gl = await bot.get_group_list()
    try:
        await bot.send_private_msg(user_id=su, message=f"开始向{len(gl)}个群广播：\n{msg}")
    except Exception as e:
        nonebot.logger.error(f'向广播发起者发送广播摘要失败：{type(e)}')
    for g in gl:
        await asyncio.sleep(0.5)
        try:
            await bot.send_group_msg(group_id=g["group_id"], message=msg)
            nonebot.logger.info(f'群{g["group_id"]} 投递广播成功')
        except ActionFailed as e:
            nonebot.logger.error(f'群{g["group_id"]} 投递广播失败：{type(e)}')
            try:
                await bot.send_private_msg(user_id=su, message=f'群{g["group_id"]} 投递广播失败：{type(e)}')
            except Exception as e:
                nonebot.logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')
    await bot.send_private_msg(user_id=su, message='广播完成！')
