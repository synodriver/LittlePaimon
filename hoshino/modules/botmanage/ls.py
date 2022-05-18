import nonebot
from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, Bot


async def ls_group(bot: Bot, event: MessageEvent):
    self_ids = bot.get_self_ids()
    for sid in self_ids:
        gl = await bot.get_group_list(self_id=sid)
        msg = ["{group_id} {group_name}".format_map(g) for g in gl]
        msg = "\n".join(msg)
        msg = f"bot:{sid}\n| 群号 | 群名 | 共{len(gl)}个群\n{msg}"
        await bot.send_private_msg(self_id=sid, user_id=int(list(bot.config.SUPERUSERS)[0]), message=msg)


async def ls_friend(bot: Bot, event: MessageEvent):
    gl = await bot.get_friend_list()
    msg = ["{user_id} {nickname}".format_map(g) for g in gl]
    msg = "\n".join(msg)
    msg = f"| QQ号 | 昵称 | 共{len(gl)}个好友\n{msg}"
    await bot.send(event, msg)


# async def ls_service(bot: Bot, service_name: str):
#     all_services = Service.get_loaded_services()
#     if service_name in all_services:
#         sv = all_services[service_name]
#         on_g = '\n'.join(map(str, sv.enable_group))
#         off_g = '\n'.join(map(str, sv.disable_group))
#         default_ = 'enabled' if sv.enable_on_default else 'disabled'
#         msg = f"服务{sv.name}：\n默认：{default_}\nuse_priv={sv.use_priv}\nmanage_priv={sv.manage_priv}\nvisible={sv.visible}\n启用群：\n{on_g}\n禁用群：\n{off_g}"
#         event.finish(msg)
#     else:
#         event.finish(f'未找到服务{service_name}')


async def ls_bot(bot: Bot, event: MessageEvent):
    self_ids = nonebot.get_bots()
    await bot.send(event, f"共{len(self_ids)}个bot\n{list(self_ids.values())}")


parser = ArgumentParser()
parser.add_argument('-g', '--group', action='store_true')
parser.add_argument('-f', '--friend', action='store_true')
parser.add_argument('-b', '--bot', action='store_true')
parser.add_argument('-s', '--service')

matcher = on_shell_command("ls", parser=parser)


@matcher.handle()
async def ls(bot: Bot, event: MessageEvent, state: dict):
    args = state["_args"]
    if args.group:
        await ls_group(bot)
    elif args.friend:
        await ls_friend(bot)
    elif args.bot:
        await ls_bot(bot)
    # elif args.service:
    #     await ls_service(bot, args.service)
