import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

m = on_command('清理数据')


@m.handle()
async def clean_image(event: MessageEvent):
    # fixme 清理数据
    if event.is_tome():
        await m.send('Image 文件夹已清理')
