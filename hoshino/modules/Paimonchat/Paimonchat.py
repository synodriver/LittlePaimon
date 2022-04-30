from pathlib import Path

import nonebot
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, GroupMessageEvent
from nonebot import logger, MatcherGroup
from nonebot.exception import ActionFailed

import hoshino
from hoshino.util import filt_message, PriFreqLimiter
import random, os, json, datetime, re
from os import path

lmt = PriFreqLimiter(30)

# sv = hoshino.Service('派蒙聊天')
sv = MatcherGroup()
logger = nonebot.logger
res_dir = path.join(path.dirname(__file__), 'res')

# 不进行复读的关键词
ban_word = ['禁言', 'ys', 'ssbq', '十连', 'sy', '原神']
# 派蒙聊天关键词的配置，第一个为冷却时间，单位秒，第二个为触发概率
word_config = {
    '确实': (60, 0.6),
    '坏了': (60, 0.6),
    '诶嘿': (180, 0.5),
    '进不去': (240, 0.5),
    '派蒙是谁': (480, 1),
    '大佬': (300, 0.6),
    '好色': (300, 0.5),
    '无语': (300, 0.6),
    '祝福': (480, 1),
    '相信': (600, 0.5),
    '憨批': (480, 0.5),
    '可爱': (480, 0.5),
    '绿茶': (600, 1),
    '不是吧': (300, 0.5),
    '好耶': (180, 0.75),
    '好听': (600, 0.4),
    '耽误时间': (600, 0.6),
    '不可以': (180, 0.6),
    '好意思': (300, 0.5),
    '不要啊': (180, 0.5),
    '羡慕': (180, 0.5),
    '过分': (300, 0.5),
    '不明白': (300, 0.5),
    '哪里不对': (300, 0.5)
}

PROB_A = 1.6
group_stat = {}
check_rep = {}

matcher1 = sv.on_message()


@matcher1.handle()
async def random_repeater(bot: Bot, event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        gid = str(event.group_id)
    elif event.message_type == 'guild':
        gid = str(event.channel_id)
    else:
        return
    msg = str(event.message)

    if gid not in group_stat:
        group_stat[gid] = (msg, False, 0)
        return
    if gid not in check_rep:
        check_rep[gid] = False

    last_msg, is_repeated, p = group_stat[gid]
    if last_msg == msg and not any(w in msg for w in ban_word):  # 群友正在复读 fixme 应该是w in msg吧
        check_rep[gid] = True
        if not is_repeated:  # 机器人尚未复读过，开始测试复读
            if random.random() < p:  # 概率测试通过，复读并设flag
                try:
                    group_stat[gid] = (msg, True, 0)
                    await bot.send(event, filt_message(event.message))
                except ActionFailed as e:
                    logger.error(f'复读失败: {type(e)}')
                    logger.exception(e)
            else:  # 概率测试失败，蓄力
                p = 1 - (1 - p) / PROB_A
                group_stat[gid] = (msg, False, p)
    else:  # 不是复读，重置
        group_stat[gid] = (msg, False, 0)
        check_rep[gid] = False


matcher2 = sv.on_message()


@matcher2.handle()
async def paimonchat(bot: Bot, event: MessageEvent):
    if event.message_type == 'group':
        gid = str(event.group_id)
    elif event.message_type == 'guild':
        return
    else:
        gid = str(event.user_id)
    msg = str(event.message)

    # 如果当前在判断复读，则不触发语音聊天
    if gid not in check_rep:
        check_rep[gid] = False
    if check_rep[gid]:
        return

    if re.match(r'.*派蒙.*坏.*', msg):
        word = '坏了'
        reply = random.choice(['你才坏！', '瞎说啥呢？', '派蒙怎么可能会坏！']) + '[CQ:face,id=146]'
    elif re.match(r'.*(雀食|确实).*', msg):
        word = '确实'
        reply = '雀食' if '雀食' in msg else '确实'
    elif re.match(r'.*(诶嘿|哎嘿|欸嘿).*', msg):
        word = '诶嘿'
        path = res_dir + random.choice(['/诶嘿.mp3', '/诶嘿cn.mp3'])
        # reply = f'[CQ:record,file=file:///{path}]'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*进不?(来|去).*', msg):
        word = '进不去'
        path = res_dir + '/进不去.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*(派蒙.*是(什么|谁))|((什么|谁)是?.*派蒙).*', msg):
        word = '派蒙是谁'
        path = res_dir + random.choice(['/嘿嘿你猜.mp3', '/中二派蒙.mp3', '/伙伴.mp3'])
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*((大|巨)佬)|带带|帮帮|邦邦.*', msg):
        word = '大佬'
        path = res_dir + '/大佬nb.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*好色|变态(哦|噢)?', msg):
        word = '好色'
        path = res_dir + random.choice(['/好色哦.mp3', '/好变态.mp3'])
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*(\.{3,9})|(\。{3,9})|无语|无话可说.*', msg):
        word = '无语'
        path = res_dir + random.choice(['/无语.mp3', '/冷淡反应.mp3'])
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*派蒙.*(祝福|吟唱|施法).*', msg):
        word = '祝福'
        path = res_dir + '/来个祝福.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*信?不信|信我.*', msg):
        word = '相信'
        path = res_dir + random.choice(['/我信你个鬼.mp3', '/真的假的.mp3'])
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*(憨批|傻(逼|B|b)).*', msg):
        word = '憨批'
        path = res_dir + '/憨批.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*可爱|卡哇伊', msg):
        word = '可爱'
        path = res_dir + '/真是个小可爱.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*派蒙.*(giegie|绿茶).*', msg):
        word = '绿茶'
        path = res_dir + '/绿茶派.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'不(是|会)吧', msg):
        word = '不是吧'
        path = res_dir + '/不是吧阿sir.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'好耶|太(好|棒)(了|啦)|好(\!|\！)', msg):
        word = '好耶'
        path = res_dir + random.choice(['/好耶.mp3', '/太好啦.mp3'])
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'(好|真|非常)?好听(\!|\！)?', msg):
        word = '好听'
        path = res_dir + '/好听.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'快{1,4}|gkd|搞?快点|赶紧的?|(.*耽误.*时间.*)', msg):
        word = '耽误时间'
        path = res_dir + '/耽误时间.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'不(可以|行|能)(吧|的|噢)?', msg):
        word = '不可以'
        path = res_dir + '/不可以.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'不(好|要)(吧|啊)?', msg):
        word = '不要啊'
        path = res_dir + '/不要啊.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*好意思.*', msg):
        word = '好意思'
        path = res_dir + '/好意思.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*羡慕.*', msg):
        word = '羡慕'
        path = res_dir + '/羡慕.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*过分.*', msg):
        word = '过分'
        path = res_dir + '/好过分.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'.*明白.*', msg):
        word = '不明白'
        path = res_dir + '/不明白.mp3'
        reply = MessageSegment.record(file=Path(path))
    elif re.match(r'(是|对)(吧|吗)', msg):
        word = '哪里不对'
        path = res_dir + '/哪里不对.mp3'
        reply = MessageSegment.record(file=Path(path))
    else:
        return
    if not lmt.check(gid, word):  # 判断是否在冷却
        return
    elif random.random() < word_config[word][1]:  # 判断概率是否触发
        try:
            await bot.send(event, reply)
            lmt.start_cd(gid, word, word_config[word][0])  # 开始冷却
        except:
            logger.error('派蒙聊天语音发送失败，请检查是否已安装ffmpeg')
