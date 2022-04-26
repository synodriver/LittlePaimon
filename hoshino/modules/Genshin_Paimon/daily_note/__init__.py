import re
from json import JSONDecodeError
from datetime import datetime, timedelta
from asyncio import sleep

import nonebot
from nonebot import logger, MatcherGroup, get_bot
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.exception import ActionFailed

from ..util import get_uid_in_msg
from ..get_data import get_daily_note_data
from .get_img import draw_daily_note_card
from ..db_util import update_note_remind2, update_note_remind, get_note_remind, delete_note_remind, \
    update_day_remind_count

from ..config import remind_time_start, remind_time_end, remind_check_time, remind_limit_count

help_msg = '''
[ssbq/实时便签 (uid)]查询当前树脂、洞天宝钱、派遣状况等
[ssbq (uid) 开启提醒(树脂数)/关闭提醒]开启/关闭树脂提醒，达到树脂数时会在群里艾特你
*绑定私人cookie之后才能使用
'''
# sv = Service('派蒙实时便签', bundle='派蒙', help_=help_msg)
sv = MatcherGroup()

matcher1 = sv.on_startswith(('ssbq', '实时便笺', '实时便签'))


@matcher1.handle()
async def main(bot: Bot, event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
    else:
        gid = str(event.user_id)
    uid, msg, user_id, use_cache = await get_uid_in_msg(event)
    find_remind_enable = re.search(r'(?P<action>开启提醒|关闭提醒|删除提醒)\s*((?P<num>\d{1,3})|(?:.*))', msg)
    if find_remind_enable:
        if event.message_type == 'guild':
            await bot.send(event, '实时便签提醒功能暂时无法在频道内使用哦')
            return
        if find_remind_enable.group('action') == '开启提醒':
            if find_remind_enable.group('num'):
                await update_note_remind2(user_id, uid, gid, 1, find_remind_enable.group('num'))
                await bot.send(event, f'开启提醒成功,派蒙会在你的树脂达到{find_remind_enable.group("num")}时提醒你的', at_sender=True)
            else:
                await update_note_remind2(user_id, uid, gid, 1)
                await bot.send(event, '开启提醒成功', at_sender=True)
        elif find_remind_enable.group('action') == '关闭提醒':
            await bot.send(event, '关闭提醒成功', at_sender=True)
            await update_note_remind2(user_id, uid, gid, 0)
        elif find_remind_enable.group('action') == '删除提醒':
            await bot.send(event, '删除提醒成功', at_sender=True)
            await delete_note_remind(user_id, uid)
    else:
        try:
            data = await get_daily_note_data(uid)
            if isinstance(data, str):
                await bot.send(event, data, at_sender=True)
            else:
                daily_note_card = await draw_daily_note_card(data, uid)
                await bot.send(event, daily_note_card, at_sender=True)
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


scheduler = nonebot.require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job('cron', minute=f'*/{remind_check_time}')
async def check_note():
    now_time = datetime.now()
    start_time = datetime(now_time.year, now_time.month, now_time.day, remind_time_start, 0, 0)
    end_time = datetime(now_time.year, now_time.month, now_time.day, remind_time_end, 0, 0)
    if start_time < now_time < end_time:
        return
    data = await get_note_remind()
    if data:
        logger.info('---派蒙开始检查实时便签树脂提醒---')
        for user_id, uid, count, remind_group, enable, last_remind_time, today_remind_count in data:
            if last_remind_time:
                last_remind_time = datetime.strptime(last_remind_time, '%Y%m%d %H:%M:%S')
                if now_time - last_remind_time > timedelta(minutes=30):
                    time_e = True
                else:
                    time_e = False
            else:
                time_e = True
            if enable and ((
                                   today_remind_count and today_remind_count < remind_limit_count) or not today_remind_count) and time_e:
                now_data = await get_daily_note_data(uid)
                if isinstance(now_data, str):
                    try:
                        await delete_note_remind(user_id, uid)
                        if user_id == remind_group:
                            await get_bot().send_private_msg(user_id=user_id,
                                                             message=MessageSegment.at(
                                                                 user_id) + f'你的cookie失效了哦,派蒙没办法帮你检查树脂,请重新添加ck后再叫派蒙开启提醒')
                        else:
                            await get_bot().send_group_msg(group_id=remind_group,
                                                           message=MessageSegment.at(
                                                               user_id) + f'你的cookie失效了哦,派蒙没办法帮你检查树脂,请重新添加ck后再叫派蒙开启提醒')
                    except Exception as e:
                        logger.error(f'---派蒙发送树脂提醒失败:{e}---')
                else:
                    if now_data['data']['current_resin'] >= count:
                        logger.info(f'---用户{user_id}的uid{uid}的树脂已经达到阈值了,发送提醒---')
                        if today_remind_count:
                            today_remind_count += 1
                        else:
                            today_remind_count = 1
                        now_time_str = now_time.strftime('%Y%m%d %H:%M:%S')
                        try:
                            await update_note_remind(user_id, uid, count, remind_group, enable, now_time_str,
                                                     today_remind_count)
                            if user_id == remind_group:
                                await get_bot().send_private_msg(user_id=user_id,
                                                                 message=MessageSegment.at(
                                                                     user_id) + f'⚠️你的树脂已经达到了{now_data["data"]["current_resin"]},记得清理哦!⚠️')
                            else:
                                await get_bot().send_group_msg(group_id=remind_group,
                                                               message=MessageSegment.at(
                                                                   user_id) + f'⚠️你的树脂已经达到了{now_data["data"]["current_resin"]},记得清理哦!⚠️')
                        except Exception as e:
                            logger.error(f'---派蒙发送树脂提醒失败:{e}---')
                await sleep(3)


scheduler.scheduled_job('cron', hour='0')


async def delete_day_limit():
    logger.info('---清空今日树脂提醒限制---')
    await update_day_remind_count()


matcher2 = sv.on_startswith("help")


@matcher2.handle()
async def handle_help(bot: Bot):
    await matcher2.send(help_msg)
