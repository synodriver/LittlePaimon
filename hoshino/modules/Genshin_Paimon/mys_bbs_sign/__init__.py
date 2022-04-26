import nonebot
from nonebot import logger, MatcherGroup, get_bot
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, GroupMessageEvent

from ..util import get_uid_in_msg
from ..db_util import get_auto_sign, add_auto_sign, delete_auto_sign
from ..get_data import get_sign_info, sign, get_sign_list
from ..config import auto_sign_time
from datetime import datetime
from asyncio import sleep
import random
from collections import defaultdict
import re

# sv = Service('派蒙米游社自动签到', bundle='派蒙')
sv = MatcherGroup()

matcher1 = sv.on_startswith(('mys签到', 'mys-sign'))


@matcher1.handle()
async def bbs_ys_sign(bot: Bot, event: MessageEvent):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event)
    sign_list = await get_sign_list()
    sign_info = await get_sign_info(uid)
    if isinstance(sign_info, str):
        await bot.send(event, sign_info, at_sender=True)
    elif sign_info['data']['is_sign']:
        sign_day = sign_info['data']['total_sign_day'] - 1
        await bot.send(event,
                       f'你今天已经签过到了哦,获得的奖励为:\n{sign_list["data"]["awards"][sign_day]["name"]} * {sign_list["data"]["awards"][sign_day]["cnt"]}',
                       at_sender=True)
    else:
        sign_day = sign_info['data']['total_sign_day']
        sign_action = await sign(uid)
        if isinstance(sign_action, str):
            await bot.send(event, sign_action, at_sender=True)
        else:
            await bot.send(event,
                           f'签到成功,获得的奖励为:\n{sign_list["data"]["awards"][sign_day]["name"]} * {sign_list["data"]["awards"][sign_day]["cnt"]}',
                           at_sender=True)


matcher2 = sv.on_startswith(('mys自动签到', '米游社自动签到', 'mys-auto-sign'))


@matcher2.handle()
async def bbs_auto_sign(bot: Bot, event: MessageEvent):
    if not isinstance(event, GroupMessageEvent):
        await bot.send(event, '自动签到功能暂时只限Q群内使用哦')
        return
    msg = event.message.extract_plain_text().strip()
    find_uid = re.search(r'(?P<uid>(1|2|5)\d{8})', msg)
    if not find_uid:
        await bot.send(event, '请把正确的需要帮忙签到的uid给派蒙哦!', at_sender=True)
    else:
        uid = find_uid.group('uid')
        find_action = re.search(r'(?P<action>开启|启用|打开|关闭|禁用)', msg)
        if find_action:
            if find_action.group('action') in ['开启', '启用', '打开']:
                await add_auto_sign(str(event.user_id), uid, str(event.group_id))
                await bot.send(event, '开启米游社自动签到成功,派蒙会在每日0点帮你签到', at_sender=True)
            elif find_action.group('action') in ['关闭', '禁用']:
                await delete_auto_sign(str(event.user_id), uid)
                await bot.send(event, '关闭米游社自动签到成功', at_sender=True)
        else:
            await add_auto_sign(str(event.user_id), uid, str(event.group_id))
            await bot.send(event, '开启米游社自动签到成功,派蒙会在每日0点帮你签到', at_sender=True)


scheduler = nonebot.require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job('cron', hour=auto_sign_time)
async def auto_sign():
    data = await get_auto_sign()
    if data:
        ann = defaultdict(lambda: defaultdict(list))
        logger.info('---派蒙开始执行米游社自动签到---')
        sign_list = await get_sign_list()
        for user_id, uid, group_id in data:
            await sleep(random.randint(3, 8))
            sign_result = await sign(uid)
            if not isinstance(sign_result, str):
                sign_info = await get_sign_info(uid)
                sign_day = sign_info['data']['total_sign_day'] - 1
                ann[group_id]['成功'].append(
                    f'.UID{uid}-{sign_list["data"]["awards"][sign_day]["name"]}*{sign_list["data"]["awards"][sign_day]["cnt"]}')
            else:
                await delete_auto_sign(user_id, uid)
                ann[group_id]['失败'].append(f'.UID{uid}')
        for group_id, content in ann.items():
            group_str = '米游社自动签到结果：\n'
            for type, ann_list in content.items():
                if ann_list:
                    group_str += f'签到{type}：\n'
                    for u in ann_list:
                        group_str += str(ann_list.index(u) + 1) + u + '\n'
            try:
                await get_bot().send_group_msg(group_id=group_id, message=group_str)
                await sleep(random.randint(3, 8))
            except Exception as e:
                logger.error(f'米游社签到结果发送失败：{e}')
