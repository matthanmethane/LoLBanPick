import collections
import json
import uuid
from typing import Union

import uvicorn
from fastapi import FastAPI, Request, Cookie, Query, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket
import enum

from starlette.staticfiles import StaticFiles

from WebsocketManager import WebsocketManager
from common.enum import Side
from logic.logic import initialize, chat_message, PICK_BAN_PHASE, PICK_BAN_SIDE

BASE_URL = "http://127.0.0.1:8000"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
wsMgr_dict = {}
ban_pick_dict = {}
phase_dict = {}


@app.get("/create")
async def create():
    token = uuid.uuid4()
    response = {side.name: f"{BASE_URL}/{side.value}/{token}" for side in Side}
    return response


async def get_cookie_or_token(
        websocket: WebSocket,
        session: Union[str, None] = Cookie(default=None),
        token: Union[str, None] = Query(default=None),
):
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.websocket("/{side}/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        side: int = 0,
        cookie_or_token: str = Depends(get_cookie_or_token),
):
    wsMgr_dict.setdefault(cookie_or_token, WebsocketManager())
    ban_pick_dict.setdefault(cookie_or_token, {})
    phase_dict.setdefault(cookie_or_token, 0)

    ws_mgr = wsMgr_dict[cookie_or_token]
    await ws_mgr.connect(websocket)
    await initialize(ws_mgr, websocket, cookie_or_token, side, ban_pick_dict[cookie_or_token],
                     phase_dict[cookie_or_token])
    while True:
        msg_json = await websocket.receive_json()
        event_type = msg_json["type"]
        if event_type == "select":
            await ws_mgr.broadcast(
                {
                    "type": event_type,
                    "phase": PICK_BAN_PHASE[phase_dict[cookie_or_token]],
                    "champ_name": msg_json["champ_name"]
                }
            )
        elif event_type == "lock_in":
            await ws_mgr.broadcast(
                {
                    "type": event_type,
                    "phase": PICK_BAN_PHASE[phase_dict[cookie_or_token]],
                    "action_side": PICK_BAN_SIDE[phase_dict[cookie_or_token] + 1] if (phase_dict[
                                                                                          cookie_or_token] + 1) < len(
                        PICK_BAN_SIDE) else "none",
                    "champ_name": msg_json["champ_name"]
                }
            )
            ban_pick_dict[cookie_or_token][PICK_BAN_PHASE[phase_dict[cookie_or_token]]] = msg_json["champ_name"]
            phase_dict[cookie_or_token] += 1
            if PICK_BAN_PHASE[phase_dict[cookie_or_token]] == "end":
                await ws_mgr.broadcast(
                    {
                        "type": "terminate",
                        "phase": PICK_BAN_PHASE[phase_dict[cookie_or_token]],
                        "champ_name": None
                    }
                )


@app.get("/{side}/{token}", response_class=HTMLResponse)
async def get(request: Request, token: str, side: int = 0):
    with open('champion_list.json', 'r', encoding='utf-8') as f:
        champion_list = json.load(f)
    return templates.TemplateResponse(
        "chat.html", {
            "request": request,
            "side_id": side,
            "side": Side(side).name,
            "token": token,
            "champion_list": champion_list
        }
    )


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
