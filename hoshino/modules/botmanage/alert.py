from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent, Bot


async def check_event(event: GroupDecreaseNoticeEvent):
    return (
        isinstance(event, GroupDecreaseNoticeEvent)
        and event.user_id == event.self_id
    )


matcher = on_notice(check_event)


@matcher.handle()
async def kick_me_alert(bot: Bot, event: GroupDecreaseNoticeEvent):
    group_id = event.group_id
    operator_id = event.operator_id
    coffee = list(bot.config.SUPERUSERS)[0]
    await bot.send_private_msg(user_id=int(coffee),
                               message=f'被Q{operator_id}踢出群{group_id}')
