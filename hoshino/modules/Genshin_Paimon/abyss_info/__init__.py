from json import JSONDecodeError

from nonebot import MatcherGroup, logger, CommandGroup
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.exception import ActionFailed
from ..util import get_uid_in_msg
from ..get_data import get_abyss_data
from .get_img import draw_abyss_card

help_msg = '''
[sy/深渊查询/深境螺旋查询 (uid) (层数)]查询深渊战绩信息
*绑定私人cookie之后才能查看层数具体阵容哦
'''
# sv = Service('派蒙深渊查询', bundle='派蒙', help_=help_msg)
sv = MatcherGroup()

matcher1 = sv.on_startswith(('sy', '深渊查询', '深境螺旋查询'))


@matcher1.handle()
async def main(bot: Bot, event: MessageEvent):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event)
    if not uid:
        await bot.send(event, '请把正确的uid给派蒙哦,例如sy100123456!', at_sender=True)
        return
    if not msg:
        floor = []
    else:
        floor = msg.split(' ')
    true_floor = []
    for f in floor:
        if f.isdigit() and (9 <= int(f) <= 12) and len(true_floor) < 2:
            true_floor.append(int(f))
    true_floor.sort()
    try:
        data = await get_abyss_data(user_id, uid, use_cache=use_cache)
        if isinstance(data, str):
            await bot.send(event, data, at_sender=True)
        else:
            abyss_card = await draw_abyss_card(data, uid, true_floor)
            await bot.send(event, abyss_card, at_sender=True)
    except ActionFailed:
        logger.exception('账号可能被风控')
        await bot.send(event, '派蒙可能被风控，发不出消息')
    except TypeError or AttributeError:
        await bot.send(event, '派蒙好像没有该UID的绑定信息')
    except IndexError or KeyError:
        await bot.send(event, '派蒙获取信息失败，可能是米游社API有变动，请联系开发者')
    except JSONDecodeError:
        await bot.send(event, '派蒙获取信息失败，重试一下吧')
    except Exception as e:
        await bot.send(event, f'派蒙出现了问题：{e}')

matcher2 = sv.on_startswith(('sy', '深渊查询', '深境螺旋查询'))