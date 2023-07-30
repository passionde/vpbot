import json

from aiogram import types
from aiogram.types import WebAppInfo

from config import HTTPS_HOST


def battle_keyboard_for_user(event_id: int, is_invitation=True) -> types.InlineKeyboardMarkup:
    url = f"{HTTPS_HOST}/web/battle.html?invitation={event_id}"
    if not is_invitation:
        url = f"{HTTPS_HOST}/web/battle.html?battle={event_id}"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📺", web_app=WebAppInfo(url=url)),
    )
    return markup


def battle_keyboard_for_opponent(invitation_id: int) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔", callback_data=json.dumps(
            {"type": "agreement", "invitation_id": invitation_id}
        )),
        types.InlineKeyboardButton(
            "📺",
            web_app=WebAppInfo(
                url=f"{HTTPS_HOST}/web/battle?invitation={invitation_id}"
            )
        ),
        types.InlineKeyboardButton("❌", callback_data=json.dumps(
            {"type": "refusal", "invitation_id": invitation_id}
        ))
    )
    return markup
