import re
import random
import datetime
from io import BytesIO
from pathlib import Path
from os import path

import aiohttp
from PIL import Image

from nonebot.adapters.onebot.v11 import MessageEvent, Bot, PokeNotifyEvent, MessageSegment
from nonebot import MatcherGroup
from nonebot.typing import T_State
from hoshino.util import FreqLimiter
from .data_source import *
from ._res import Res as R

lmt = FreqLimiter(20)

HELP_MSG = '''
头像相关表情包制作
摸摸|亲亲|吃掉|贴贴|拍拍|给爷爬|撕掉|精神支柱|扔掉|要我一直+@人/qq号/图片
戳一戳随机概率触发
'''
# sv = Service('表情包', bundle='娱乐', help_=HELP_MSG)
sv = MatcherGroup()
data_dir = path.join(path.dirname(__file__), 'resources')

matcher1 = sv.on_regex(r'^#(rua|摸摸|亲亲|吃掉|贴贴|拍拍|给爷爬|撕掉|精神支柱|扔掉|要我一直)(?P<name>.*?)$')


@matcher1.handle()
async def main(bot: Bot, event: MessageEvent, state: T_State):
    name = state['_matched']
    if event.message_type == 'guild':
        rm = str(event.message)
    else:
        rm = str(event.raw_message)
    if name == '':
        match = re.search(r"\[CQ:at,qq=(.*)\]", rm)
        if not match:
            match2 = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(event.message))
            try:
                action = rm.split('[CQ')[0].strip(' ')
                async with aiohttp.ClientSession() as session:
                    async with session.get(match2.group(2)) as resp:
                        resp_cont = await resp.read()
                head = Image.open(BytesIO(resp_cont))
            except:
                await bot.send(event, '指令出错，请艾特或接图片', at_sender=True)
                return
        else:
            if event.message_type == 'guild':
                await bot.send(event, '频道无法用艾特噢', at_sender=True)
                return
            head = await get_avatar(match.group(1))
            action = str(event.message).split('[CQ')[0].strip(' ')
    elif name.isdigit():
        head = await get_avatar(name)
        action = rm.split(name)[0].strip(' ')
    elif name == '#自己':
        head = await get_avatar(str(event.user_id))
        action = rm.split(name)[0].strip(' ')
    else:
        await bot.send(event, '指令出错，请艾特或接图片', at_sender=True)
        return
    if action == '#亲亲':
        my_head = await get_avatar(str(event.user_id))
        res = await kiss(data_dir, head, my_head)
    elif action == '#吃掉':
        res = await eat(data_dir, head)
    elif action == '#摸摸' or action == '#rua':
        res = await rua(data_dir, head)
    elif action == '#贴贴':
        my_head = await get_avatar(str(event.user_id))
        res = await rub(data_dir, head, my_head)
    elif action == '#拍拍':
        res = await pat(data_dir, head)
    elif action == '#给爷爬':
        res = await crawl(data_dir, head)
    elif action == '#撕掉':
        res = await rip(data_dir, head)
    elif action == '#精神支柱':
        res = await support(data_dir, head)
    elif action == '#扔掉':
        res = await throw(data_dir, head)
    elif action == '#要我一直':
        res = await always(data_dir, head)
    await bot.send(event, R.image(res))


async def check_poke(event: PokeNotifyEvent) -> bool:
    if isinstance(event, PokeNotifyEvent):
        return True if event.is_tome() else False
    else:
        return False


matcher2 = sv.on_notice(rule=check_poke)


@matcher2.handle()
async def poke_back(event: PokeNotifyEvent):
    uid = event.user_id
    tid = event.target_id
    gid = event.group_id
    if not lmt.check(gid):
        return
    if random.random() <= 0.5:
        if tid == event.self_id:
            if random.random() <= 0.5:
                path = data_dir + random.choice(
                    ['/这个仇.mp3', '/好生气.mp3', '/好气哦.mp3', '/好变态.mp3', '/坏蛋.mp3', '/不要啊.mp3', '/好过分.mp3'])
                res = MessageSegment.record(file=Path(path))
                await matcher2.send(res)
        else:
            if random.random() <= 0.3:
                my_head = await get_avatar(str(uid))
                head = await get_avatar(str(tid))
                res = await random.choice(data_source.avatarFunList1)(data_dir, head, my_head)
                await matcher2.send(R.image(res))
            else:
                head = await get_avatar(str(tid))
                res = await random.choice(data_source.avatarFunList2)(data_dir, head)
                await matcher2.send(R.image(res))
        lmt.start_cd(gid, 20)


async def get_avatar(qq):
    url = f'http://q1.qlogo.cn/g?b=qq&nk={qq}&s=160'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp_cont = await resp.read()
    avatar = Image.open(BytesIO(resp_cont)).convert("RGBA")
    return avatar


matcher3 = sv.on_startswith("help")


@matcher3.handle()
async def handle_help(bot: Bot):
    await matcher3.send(HELP_MSG)
