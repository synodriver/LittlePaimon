# from hoshino import Service, priv, CanceledException, logger
import nonebot
from nonebot import logger, MatcherGroup
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, GroupMessageEvent

from hoshino import priv
from ..get_data import get_bind_game
from ..db_util import insert_public_cookie, update_private_cookie, delete_cookie_cache, delete_cookie, \
    delete_private_cookie, update_last_query, reset_public_cookie
from ..util import check_cookie

help_msg = '''
1.[ysb cookie]绑定你的私人cookie以开启高级功能
2.[删除ck]删除你的私人cookie
3.[添加公共ck cookie]添加公共cookie以供大众查询*仅管理员
'''
# sv = Service('派蒙绑定', visible=False, enable_on_default=True, bundle='派蒙', help_=help_msg)
sv = MatcherGroup()

cookie_error_msg = '这个cookie无效哦，请旅行者确认是否正确\n1.ck要登录mys帐号后获取,且不能退出登录\n2.ck中要有cookie_token和account_id两个参数\n3.建议在无痕模式下取'

matcher1 = sv.on_startswith(('原神绑定', 'ysb'))


@matcher1.handle()
async def bind(bot: Bot, event: MessageEvent):
    cookie = event.message.extract_plain_text().strip()
    if cookie == '':
        res = '''旅行者好呀，你可以直接用ys/ysa等指令附上uid来使用派蒙\n如果想看全部角色信息和实时便笺等功能，要把cookie给派蒙哦\ncookie获取方法：登录网页版米游社，在地址栏粘贴代码：\njavascript:(function(){prompt(document.domain,document.cookie)})();\n复制弹窗出来的字符串（手机要via或chrome浏览器才行）\n然后添加派蒙私聊发送ysb接刚刚复制的字符串，例如:ysb UM_distinctid=17d131d...\ncookie是账号重要安全信息，请确保机器人持有者可信赖！'''
        await bot.send(event, res, at_sender=True)
    else:
        cookie_info, mys_id = await get_bind_game(cookie)
        if not cookie_info or cookie_info['retcode'] != 0:
            msg = cookie_error_msg
            if event.detail_type != 'private':
                msg += '\n当前是在群聊里绑定，建议旅行者添加派蒙好友私聊绑定!'
            await bot.send(event, msg, at_sender=True)
        else:
            for data in cookie_info['data']['list']:
                if data['game_id'] == 2:
                    uid = data['game_role_id']
                    nickname = data['nickname']
                    break
            if uid:
                await update_private_cookie(user_id=str(event.user_id), uid=uid, mys_id=mys_id, cookie=cookie)
                await update_last_query(str(event.user_id), uid, 'uid')
                await delete_cookie_cache(uid, key='uid', all=False)
                msg = f'{nickname}绑定成功啦!使用ys/ysa等指令和派蒙互动吧!'
                if event.detail_type != 'private':
                    msg += '\n当前是在群聊里绑定，建议旅行者把cookie撤回哦!'
                await bot.send(event, msg, at_sender=True)


matcher2 = sv.on_startswith('删除ck')


@matcher2.handle()
async def delete(bot: Bot, event: MessageEvent):
    user_id = str(event.user_id)
    await delete_private_cookie(str(event.user_id))
    await bot.send(event, '派蒙把你的私人cookie都删除啦!', at_sender=True)


matcher3 = sv.on_startswith('添加公共ck')


@matcher3.handle()
async def bing_public(bot: Bot, event: MessageEvent):
    if not priv.check_priv(event, priv.ADMIN):
        await bot.send(event, '只有管理员或主人才能添加公共cookie哦!')
        return
    cookie = event.message.extract_plain_text().strip()
    if await check_cookie(cookie):
        await insert_public_cookie(cookie)
        await bot.send(event, '公共cookie添加成功啦,派蒙开始工作!')
    else:
        await bot.send(event, cookie_error_msg)


scheduler = nonebot.require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job('cron', hour='0')
async def delete_cache():
    logger.info('---清空今日cookie缓存---')
    await delete_cookie_cache(all=True)
    logger.info('---清空今日cookie限制记录---')
    await reset_public_cookie()
