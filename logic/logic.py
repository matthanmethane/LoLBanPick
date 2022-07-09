from typing import List

from fastapi.websockets import WebSocket

from WebsocketManager import WebsocketManager
from common.enum import Side


async def initialize(ws_mgr: WebsocketManager, ws: WebSocket, cookie_or_token: str, msg_list: List[tuple]):
    await ws_mgr.send_personal_message(f"Connected in {cookie_or_token}", ws)
    for data in msg_list:
        await ws_mgr.send_personal_message(chat_message(*data), ws)


def chat_message(side, msg):
    return f"{Side(side).name}: {msg}"
