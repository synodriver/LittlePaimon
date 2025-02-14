# I'm free! 其实是不想改了 todo 以后来 数据库的postgre异步计划 mongodb计划 redis缓存
# import re
# import hoshino
# from hoshino import sucmd, HoshinoBot
# from nonebot.adapters.onebot.v11 import CommandSession, CQHttpError, MessageSegment as ms
#
# @sucmd('billing')
# async def billing(event: CommandSession):
#     bot = event.bot
#     args = event.current_arg_text.split()
#     try:
#         for i in range(0, len(args), 2):
#             args[i] = int(args[i])
#             assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', args[i + 1]), f"{args[i + 1]}不是合法日期"
#     except (ValueError, AssertionError) as e:
#         await event.finish(str(e))
#
#     try:
#         sid_group = {}
#         for sid in hoshino.get_self_ids():
#             gs = await bot.get_group_list(self_id=sid)
#             sid_group[sid] = [g['group_id'] for g in gs]
#     except CQHttpError as e:
#         await event.finish(str(e))
#
#     failed = []
#     not_found = []
#     for i in range(0, len(args), 2):
#         gid = args[i]
#         date = args[i + 1]
#         bill_sent_flag = False
#         for sid, groups in sid_group.items():
#             if gid in groups:
#                 msg = f"本群bot将于/已于{date}到期，请及时联系{list(hoshino.config.SUPERUSERS)[0]}续费，以免影响使用！"
#                 oid = await get_group_owner_id(bot, sid, gid)
#                 if oid:
#                     msg = str(ms.at(oid)) + msg
#                 try:
#                     await bot.send_group_msg(self_id=sid, group_id=gid, message=msg)
#                     bill_sent_flag = True
#                 except CQHttpError:
#                     failed.append(gid)
#                     try:
#                         await event.send(f"bot{sid} 向 群{gid} 发送billing失败！")
#                     except CQHttpError:
#                         hoshino.logger.critical((f"bot{sid} 向 群{gid} 发送billing失败！且回报SUPERUSER失败！"))
#         if not bill_sent_flag and gid not in failed:
#             not_found.append(gid)
#
#     msg = f"发送bill完毕！\n失败{len(failed)}：{failed}\n未找到{len(not_found)}：{not_found}"
#     await event.send(msg)
#
#
# async def get_group_owner_id(bot: HoshinoBot, self_id, group_id) -> int:
#     try:
#         members = await bot.get_group_member_list(self_id=self_id, group_id=group_id)
#     except CQHttpError:
#         return 0
#     for m in members:
#         if m.get('role') == 'owner':
#             return m.get('user_id', 0)
#     return 0
