import json

from aiogram import Dispatcher, types
from aiogram.utils import executor

from bot.keyboard import battle_keyboard_for_user
from db.alchemy.user import new_user, get_all_users
from db.models.database import async_session_maker
from bot.functions import handle_refusal, handle_agreement
from bot.notification import send_refuse_battle, send_agreement_battle
from bot.vp_bot import vp_bot

dp = Dispatcher(vp_bot)

with open("bot/hello_text.txt") as f:
    WELCOME_TEXT = f.read()


def get_type_callback(callback: types.CallbackQuery):
    return dict(json.loads(callback.data)).get("type", "")


@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    await vp_bot.send_message(msg.chat.id, WELCOME_TEXT)
    async with async_session_maker() as session:
        await new_user(session, msg.chat.id)


@dp.message_handler(commands=["users"])
async def get_all_users_handler(msg: types.Message):
    if msg.chat.id not in [478666357, 1069351042]:
        return
    async with async_session_maker() as session:
        users = await get_all_users(session)
        users = sorted(users, key=lambda u: u.rating)
        await msg.answer("\n".join(
            [f"ID: {u.user_id} Rating: {u.rating} Vpc: {u.vp_coins} DateAdd: {u.date_added}" for u in users[:10]]
        ))


@dp.callback_query_handler(lambda callback: get_type_callback(callback) == "agreement")
async def agreement_callback_handler(callback: types.CallbackQuery):
    async with async_session_maker() as session:
        msg, ok = await handle_agreement(callback, session)
        await callback.answer(msg, show_alert=True)

        if not ok:
            return

        invitation_id = dict(json.loads(callback.data)).get("invitation_id", -1)
        await callback.message.edit_text(
            f"{callback.message.text}\n[вызов принят]",
            reply_markup=battle_keyboard_for_user(invitation_id)
        )
        await send_agreement_battle(invitation_id, session)


@dp.callback_query_handler(lambda callback: get_type_callback(callback) == "refusal")
async def refusal_callback_handler(callback: types.CallbackQuery):
    async with async_session_maker() as session:
        msg, ok = await handle_refusal(callback, session)
        await callback.answer(msg, show_alert=True)

        if not ok:
            return

        invitation_id = dict(json.loads(callback.data)).get("invitation_id", -1)
        await callback.message.edit_text(
            f"{callback.message.text}\n[вызов отклонен]",
            reply_markup=battle_keyboard_for_user(invitation_id)
        )
        await send_refuse_battle(invitation_id, session)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)