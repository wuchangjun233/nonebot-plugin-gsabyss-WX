import time

from nonebot import get_bot
from nonebot.params import CommandArg
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v12 import Bot, Message, MessageEvent

from .config import plugin_config
from .draw_quickview import AbyssQuickViewDraw
from .draw_statistic import AbyssStatisticDraw
from .data_source import fetch_akasha_abyss, parse_quickview_input

PRIORITY = plugin_config.gsabyss_priority
quickview_matcher = on_command("速览",
                               aliases={"深渊速览"},
                               priority=PRIORITY,
                               block=True)
totalview_matcher = on_command("深渊统计", priority=PRIORITY, block=True)


async def file_upload(data: bytes, file_name: str):
    bot = get_bot()
    up_data = await bot.call_api(
                    'upload_file',
                    type="data",
                    data=data,
                    name=f"{file_name}",
                )
    file_id = up_data['file_id']
    return file_id


@quickview_matcher.handle()
async def abyssQuick(bot: Bot, ev: MessageEvent, arg: Message = CommandArg()):
    floor_idx, chamber_idx, schedule_key = parse_quickview_input(str(arg))
    drawer = AbyssQuickViewDraw(floor_idx, chamber_idx, schedule_key)
    res = await drawer.get_full_picture()

    async def send_file_message(res, file_type):
        params = {}
        if ev.detail_type == "group":
            params["detail_type"] = "group"
            params["group_id"] = ev.group_id
        elif ev.detail_type == "private":
            params["detail_type"] = "private"
            params["user_id"] = ev.user_id
        timestamp = time.time()
        file_name = f'_{timestamp}.png'
        file_id = await file_upload(res, file_name)
        params["message"] = [
            {"type": file_type, "data": {"file_id": file_id}}
        ]
        await bot.call_api('send_message', **params)

    await quickview_matcher.finish(
            res if isinstance(res, str)
            else await send_file_message(res.getvalue(), "image")
        )


@totalview_matcher.handle()
async def abyssTotal(bot: Bot, ev: MessageEvent, arg: Message = CommandArg()):
    if arg:
        await totalview_matcher.finish()
    akasha_data = await fetch_akasha_abyss()
    if isinstance(akasha_data, str):
        await totalview_matcher.finish(akasha_data)
    drawer = AbyssStatisticDraw(akasha_data)
    res = await drawer.get_full_picture()

    async def send_file_message(res, file_type):
        params = {}
        if ev.detail_type == "group":
            params["detail_type"] = "group"
            params["group_id"] = ev.group_id
        elif ev.detail_type == "private":
            params["detail_type"] = "private"
            params["user_id"] = ev.user_id
        timestamp = time.time()
        file_name = f'_{timestamp}.png'
        file_id = await file_upload(res, file_name)
        params["message"] = [
            {"type": file_type, "data": {"file_id": file_id}}
        ]
        await bot.call_api('send_message', **params)

    await totalview_matcher.finish(
            res if isinstance(res, str)
            else await send_file_message(res.getvalue(), "image")
        )
