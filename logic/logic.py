from typing import List, Dict

from fastapi.websockets import WebSocket

from WebsocketManager import WebsocketManager
from common.enum import Side

PICK_BAN_PHASE = [
    "redBan1",
    "blueBan1",
    "redBan2",
    "blueBan2",
    "redBan3",
    "blueBan3",
    "redPick1",
    "bluePick1",
    "bluePick2",
    "redPick2",
    "redPick3",
    "bluePick3",
    "blueBan4",
    "redBan4",
    "redBan5",
    "blueBan5",
    "bluePick4",
    "redPick4",
    "redPick5",
    "bluePick5",
    "end"
]

PICK_BAN_SIDE = [
    "red",
    "blue",
    "red",
    "blue",
    "red",
    "blue",
    "red",
    "blue",
    "blue",
    "red",
    "red",
    "blue",
    "blue",
    "red",
    "red",
    "blue",
    "blue",
    "red",
    "red",
    "blue"
]


async def initialize(
        ws_mgr: WebsocketManager,
        ws: WebSocket,
        cookie_or_token: str,
        side: int,
        ban_pick_dict: Dict[str, str],
        phase: int
):
    await ws_mgr.send_personal_message(
        {
            "type": "init",
            "phase": phase,
            "action_side": PICK_BAN_SIDE[phase],
        },
        ws
    )
    # await ws_mgr.send_personal_message(f"Connected as {Side(side).name} in {cookie_or_token}", ws)
    for phase, champion_name in ban_pick_dict.items():
        await ws_mgr.send_personal_message(
            {
                "type": "initBanPick",
                "phase_name": phase,
                "champ_name": champion_name
            },
            ws
        )
    pass


def chat_message(side, msg):
    return f"{Side(side).name}: {msg}"
