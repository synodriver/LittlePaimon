import re
import random

from nonebot import MatcherGroup
from nonebot.adapters.onebot.v11 import Event, Bot, MessageEvent
from hoshino.util import filt_message

# sv = Service('掷骰子', help_='''
# [.r] 掷骰子
# [.r 3d12] 掷3次12面骰子
# '''.strip())
sv = MatcherGroup()


async def do_dice(bot: Bot, ev: MessageEvent, num, min_, max_, opr, offset, TIP="的掷骰结果是："):
    if num == 0:
        await bot.send(ev, '咦？我骰子呢？')
        return
    min_, max_ = min(min_, max_), max(min_, max_)
    rolls = list(map(lambda _: random.randint(min_, max_), range(num)))
    sum_ = sum(rolls)
    rolls_str = '+'.join(map(lambda x: str(x), rolls))
    if len(rolls_str) > 100:
        rolls_str = str(sum_)
    res = sum_ + opr * offset
    msg = [
        f'{TIP}\n', str(num) if num > 1 else '', 'D',
        f'{min_}~' if min_ != 1 else '', str(max_),
        (' +-'[opr] + str(offset)) if offset else '',
        '=', rolls_str, (' +-'[opr] + str(offset)) if offset else '',
        f'={res}' if offset or num > 1 else '',
    ]
    msg = ''.join(msg)
    await bot.send(ev, msg, at_sender=True)


matcher1 = sv.on_regex(
    r'^\.r\s*((?P<num>\d{0,2})d((?P<min>\d{1,4})~)?(?P<max>\d{0,4})((?P<opr>[+-])(?P<offset>\d{0,5}))?)?\b',
    re.I)


@matcher1.handle()
async def dice(bot: Bot, event: MessageEvent, state: dict):
    num, min_, max_, opr, offset = 1, 1, 100, 1, 0
    match: dict = state['_matched_dict']
    if s := match.get('num'):
        num = int(s)
    if s := match.get('min'):
        min_ = int(s)
    if s := match.get('max'):
        max_ = int(s)
    if s := match.get('opr'):
        opr = -1 if s == '-' else 1
    if s := match.get('offset'):
        offset = int(s)
    await do_dice(bot, event, num, min_, max_, opr, offset)


matcher2 = sv.on_startswith('.qj')


@matcher2.handle()
async def kc_marriage(bot: Bot, ev: MessageEvent):
    wife: str = filt_message(ev.message.extract_plain_text().strip())
    tip = f'与{wife}的ケッコンカッコカリ结果是：' if wife else '的ケッコンカッコカリ结果是：'
    await do_dice(bot, ev, 1, 3, 6, 1, 0, tip)
