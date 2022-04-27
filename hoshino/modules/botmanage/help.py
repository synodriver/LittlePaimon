from io import StringIO

import nonebot

from hoshino import __version__
from nonebot.adapters.onebot.v11 import MessageEvent, Bot
from nonebot import on_startswith, MatcherGroup

# sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)
sv = MatcherGroup()

TOP_MANUAL = f'''
====================
= 惜月的小派蒙{__version__} =
发送[]内的关键词触发
有#的，#也要输入
带*号的仅绑定cookie后可用
====== 常用指令 ======
[ys uid]原神个人信息卡片
[ysa uid]原神角色背包一览
[ysc uid 角色名]原神角色详情
[sy uid]原神个人深渊信息
*[ssbq]原神实时便签
*[myzj 月份]原神每月札记
[抽n十连xx]原神模拟抽卡
[code 语言 (-i) (输入) 代码]运行代码
[#亲亲/贴贴/拍拍/给爷爬/吃掉/扔掉/撕掉/精神支柱
/要我一直+@人/qq号/图片]:好玩的gif图表情包生成
发送[#帮助派蒙]获取更详细的指令
=====================
'''.strip()


# [#喜加一资讯 n]查看n条喜加一资讯

def gen_service_manual(service: "Service", gid: int):
    spit_line = '=' * max(0, 18 - len(service.name))
    manual = [f"|{'○' if service.check_enabled(gid) else '×'}| {service.name} {spit_line}"]
    if service.help:
        manual.append(service.help)
    return '\n'.join(manual)


def gen_bundle_manual(name: str, plugin: nonebot.plugin.Plugin) -> str:
    manual = StringIO()
    manual.write(name)
    if doc := plugin.module.__doc__:
        manual.write("\n" + doc)
    return manual.getvalue()


matcher1 = sv.on_startswith('#帮助')


@matcher1.handle()
async def send_help(bot: Bot, event: MessageEvent):
    arg = event.message.extract_plain_text().strip()
    plugins = nonebot.get_loaded_plugins()
    # services = Service.get_loaded_services()
    if not arg:
        await bot.send(event, TOP_MANUAL)
    elif arg in map(lambda p: p.name, plugins):
        msg = gen_bundle_manual(arg, nonebot.get_plugin(arg))
        await bot.send(event, msg)
    # elif arg in services:
    #     s = services[arg]
    #     msg = gen_service_manual(s, gid)
    #     await bot.send(event, msg)
    # else: ignore
