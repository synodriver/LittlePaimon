import nonebot
from nonebot import on_request, on_notice
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, PokeNotifyEvent, MessageSegment, GroupRequestEvent, \
    GroupIncreaseNoticeEvent
from nonebot import MatcherGroup


async def check_invite(event: GroupRequestEvent) -> bool:
    return event.sub_type == "invite"


matcher1 = on_request(check_invite)


@matcher1.handle()
async def handle_group_invite(event: GroupRequestEvent):
    if str(event.user_id) in nonebot.get_bot().config.SUPERUSERS:
        await event.approve()
    else:
        await event.reject(reason='邀请入群请联系维护组')


matcher2 = on_notice()


@matcher2.handle()
async def handle_unknown_group_invite(event: GroupIncreaseNoticeEvent):
    if event.user_id != event.self_id:
        return
    try:
        await nonebot.get_bot().send_private_msg(user_id=int(list(nonebot.get_bot().config.SUPERUSERS)[0]),
                                                 message=f'群{event.group_id}未经允许拉了派蒙进群')
    except Exception as e:
        print('处理群聊邀请错误:', e)
