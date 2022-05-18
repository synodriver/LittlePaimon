import json
import os
import re
import nonebot
from nonebot import logger, MatcherGroup, get_bot
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, GroupMessageEvent

from ..util import get_uid_in_msg
from .gacha_logs import get_data
from .get_img import get_gacha_log_img
from .api import toApi, checkApi

help_msg = '''
1.[获取抽卡记录 (uid) (url)]提供url，获取原神抽卡记录，需要一定时间
2.[查看抽卡记录 (uid)]查看抽卡记录分析
3.[导出抽卡记录 (uid) (xlsx/json)]导出抽卡记录文件，上传到群文件中
'''
# sv = Service('派蒙抽卡记录导出', bundle='派蒙', help_=help_msg)
sv = MatcherGroup()

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data', 'gacha_log_data')
if not os.path.exists(data_path):
    os.makedirs(data_path)
if not os.path.exists(os.path.join(data_path, 'user_gacha_log.json')):
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'w', encoding='UTF-8') as f:
        json.dump({}, f, ensure_ascii=False)

matcher1 = sv.on_startswith(('导出抽卡记录', 'dcckjl', 'exportgachalog'))


@matcher1.handle()
async def ckjl(bot: Bot, event: MessageEvent):
    if event.message_type != 'group':
        await bot.send(event, '在群聊中才能导出抽卡记录文件哦！')
        return
    uid, msg, user_id, use_cache = await get_uid_in_msg(event)
    if not uid:
        await bot.send(event, '请把uid给派蒙哦，比如导出抽卡记录100000001 xlsx', at_sender=True)
        return
    find_filetype = r'(?P<filetype>xlsx|json)'
    match = re.search(find_filetype, msg)
    filetype = match['filetype'] if match else 'xlsx'
    if filetype == 'xlsx':
        filetype = f'gachaExport-{uid}.xlsx'
    else:
        filetype = f'UIGF_gachaData-{uid}.json'
    local_data = os.path.join(data_path, filetype)
    if not os.path.exists(local_data):
        await bot.send(event, '你在派蒙这里还没有抽卡记录哦，使用 更新抽卡记录 吧！', at_sender=True)
        return
    await bot.upload_group_file(group_id=event.group_id, file=local_data, name=filetype)


matcher2 = sv.on_startswith(('更新抽卡记录', '获取抽卡记录', 'updategachalog', 'gxckjl'))


@matcher2.handle()
async def update_ckjl(bot: Bot, event: MessageEvent):
    uid, msg, user_id, use_cache = await get_uid_in_msg(event)
    if not uid:
        await bot.send(event, '请把uid给派蒙哦，比如获取抽卡记录100000001 链接', at_sender=True)
        return
    if msg:
        if match := re.search(r'(https://webstatic.mihoyo.com/.*#/log)', msg):
            url = str(match[1])
        else:
            await bot.send(event, '你这个抽卡链接不对哦，应该是以https://开头、#/log结尾的！', at_sender=True)
            return
    else:
        with open(os.path.join(data_path, 'user_gacha_log.json'), 'r', encoding="utf-8") as f:
            user_data = json.load(f)
            if user_id in user_data and uid in user_data[user_id]:
                url = user_data[user_id][uid]
                await bot.send(event, '发现历史抽卡记录链接，尝试使用...')
            else:
                await bot.send(event, '拿到游戏抽卡记录链接后，对派蒙说[获取抽卡记录 uid 链接]就可以啦\n获取抽卡记录链接的方式和vx小程序的是一样的，还请旅行者自己搜方法',
                               at_sender=True)
                return
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'r', encoding="utf-8") as f:
        user_data = json.load(f)
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][uid] = url
    with open(os.path.join(data_path, 'user_gacha_log.json'), 'w', encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, sort_keys=False, indent=4)

    url = toApi(url)
    apiRes = await checkApi(url)
    if apiRes != 'OK':
        await bot.send(event, apiRes, at_sender=True)
        return
    await bot.send(event, '抽卡记录开始获取，请给派蒙一点时间...')
    await get_data(url)

    local_data = os.path.join(data_path, f'gachaData-{uid}.json')
    with open(local_data, 'r', encoding="utf-8") as f:
        gacha_data = json.load(f)
    gacha_img = await get_gacha_log_img(gacha_data, 'all')
    await bot.send(event, gacha_img, at_sender=True)


matcher3 = sv.on_startswith(('查看抽卡记录', 'ckjl', 'gachalog'))


@matcher3.handle()
async def get_ckjl(bot: Bot, event: MessageEvent):
    uid, msg, user_id, use_cache = get_uid_in_msg(event)
    if not uid:
        await bot.send(event, '请把uid给派蒙哦，比如获取抽卡记录100000001 链接', at_sender=True)
        return
    match = re.search(r'(all|角色|武器|常驻|新手)', msg)
    pool = match[1] if match else 'all'
    local_data = os.path.join(data_path, f'gachaData-{uid}.json')
    if not os.path.exists(local_data):
        await bot.send(event, '你在派蒙这里还没有抽卡记录哦，对派蒙说 获取抽卡记录 吧！', at_sender=True)
        return
    with open(local_data, 'r', encoding="utf-8") as f:
        gacha_data = json.load(f)
    gacha_img = await get_gacha_log_img(gacha_data, pool)
    await bot.send(event, gacha_img, at_sender=True)


matcher4 = sv.on_startswith("help")


@matcher4.handle()
async def handle_help():
    await matcher4.send(help_msg)
