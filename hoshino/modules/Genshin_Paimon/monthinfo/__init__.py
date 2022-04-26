import re
import datetime
from json import JSONDecodeError

from nonebot import logger, MatcherGroup
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.exception import ActionFailed
from hoshino.util import filt_message
from ..util import get_uid_in_msg
from ..get_data import get_monthinfo_data
from .get_img import draw_monthinfo_card

help_msg = '''
[myzj/每月札记/zj (uid) (月份)]查看该月份获得的原石、摩拉数
*绑定私人cookie之后才能使用,只能查看最近3个月的记录,默认为本月
'''
# sv = Service('派蒙每月札记', bundle='派蒙', help_=help_msg)

sv = MatcherGroup()

matcher1 = sv.on_startswith(('myzj', '每月札记', 'zj'))


@matcher1.handle()
async def main(bot: Bot, event: MessageEvent):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event)
    # 札记只能查看最近3个月的，构造正则来获取月份
    month_now = datetime.datetime.now().month
    if month_now == 1:
        month_list = ['11', '12', '1']
    elif month_now == 2:
        month_list = ['12', '1', '2']
    else:
        month_list = [str(month_now - 2), str(month_now - 1)]
    find_month = '(?P<month>' + '|'.join(month_list) + ')'
    match = re.search(find_month, msg)
    month = match.group('month') if match else month_now
    try:
        data = await get_monthinfo_data(uid, month, use_cache=use_cache)
        if isinstance(data, str):
            await bot.send(event, data, at_sender=True)
        else:
            monthinfo_card = await draw_monthinfo_card(data)
            await bot.send(event, monthinfo_card, at_sender=True)
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


matcher2 = sv.on_startswith("help")


@matcher2.handle()
async def handle_help(bot: Bot):
    await matcher2.send(help_msg)
