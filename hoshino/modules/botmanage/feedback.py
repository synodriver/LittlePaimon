import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, PokeNotifyEvent, MessageSegment
from nonebot import MatcherGroup

from hoshino.util import DailyNumberLimiter

# sv = Service('_feedback_', manage_priv=priv.SUPERUSER, help_='[#来杯咖啡] 后接反馈内容 联系维护组')
sv = MatcherGroup()

_max = 1
lmt = DailyNumberLimiter(_max)
EXCEED_NOTICE = f'您今天已经喝过{_max}杯了，请明早5点后再来！'

matcher1 = sv.on_startswith('#来杯咖啡')


@matcher1.handle()
async def feedback(bot: Bot, event: MessageEvent):
    uid = event.user_id
    if not lmt.check(uid):
        await bot.finish(event, EXCEED_NOTICE, at_sender=True)
    coffee = list(nonebot.get_driver().config.SUPERUSERS)[0]
    if text := str(event.message).strip():
        await bot.send_private_msg(self_id=event.self_id, user_id=int(coffee), message=f'Q{uid}@群{event.group_id}\n{text}')
        await bot.send(event, f'您的反馈已发送至维护组！\n======\n{text}', at_sender=True)
        lmt.increase(uid)
    else:
        await bot.send(event, "请发送来杯咖啡+您要反馈的内容~", at_sender=True)
