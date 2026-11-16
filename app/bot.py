import logging
import re
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from app.ai_analysis import analyze_screenshot
from app.config import settings
from app.db import db
from app.texts import t

log = logging.getLogger(__name__)
router = Router()

def main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "button_instruction")), KeyboardButton(text=t(lang, "button_language"))],
            [KeyboardButton(text=t(lang, "button_signal"))],
        ],
        resize_keyboard=True,
    )


def language_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "language_russian"), callback_data="lang:ru"),
         InlineKeyboardButton(text=t(lang, "language_english"), callback_data="lang:en")]
    ])


async def user_language(user_id: int) -> str:
    row = await db.get_user(user_id)
    return row["language"] if row else "ru"


def admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


async def referral_button(user_id: int, lang: str):
    base = await db.get_setting("referral_url")
    if not base:
        return None, None
    click_id = await db.create_referral(user_id)
    encoded = quote(click_id, safe="")
    if "{click_id}" in base:
        url = base.replace("{click_id}", encoded)
    elif "{sub1}" in base:
        url = base.replace("{sub1}", encoded)
    else:
        separator = "&" if "?" in base else "?"
        url = f"{base}{separator}sub1={encoded}"
    label = "Зарегистрироваться" if lang == "ru" else "Register"
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=label, url=url)]])
    return markup, click_id


@router.message(CommandStart())
async def start(message: Message) -> None:
    if not message.from_user:
        return
    await db.ensure_user(message.from_user.id)
    lang = await user_language(message.from_user.id)
    await message.answer(t(lang, "welcome") + "\n\n" + t(lang, "menu"), reply_markup=main_keyboard(lang))


@router.message(Command("admin"))
async def admin_help(message: Message) -> None:
    if message.from_user and admin(message.from_user.id):
        await message.answer(t(await user_language(message.from_user.id), "admin_help"))


@router.message(Command("set_referral"))
async def set_referral(message: Message) -> None:
    if not message.from_user or not admin(message.from_user.id):
        return
    value = (message.text or "").partition(" ")[2].strip()
    if not value or not value.startswith(("https://", "http://")):
        await message.answer(t(await user_language(message.from_user.id), "set_referral_usage"))
        return
    await db.set_setting("referral_url", value)
    await message.answer(t(await user_language(message.from_user.id), "saved"))


@router.message(Command("set_promo"))
async def set_promo(message: Message) -> None:
    if not message.from_user or not admin(message.from_user.id):
        return
    value = (message.text or "").partition(" ")[2].strip()
    if not value:
        await message.answer(t(await user_language(message.from_user.id), "set_promo_usage"))
        return
    await db.set_setting("promo", "" if value == "-" else value)
    await message.answer(t(await user_language(message.from_user.id), "saved"))


@router.message(Command("get_referral"))
async def get_referral(message: Message) -> None:
    if not message.from_user or not admin(message.from_user.id):
        return
    value = await db.get_setting("referral_url")
    await message.answer(value or t(await user_language(message.from_user.id), "referral_unset"))


@router.message(Command("get_promo"))
async def get_promo(message: Message) -> None:
    if not message.from_user or not admin(message.from_user.id):
        return
    value = await db.get_setting("promo")
    await message.answer(value or t(await user_language(message.from_user.id), "promo_unset"))


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return
    lang = callback.data.partition(":")[2]
    if lang not in ("ru", "en"):
        await callback.answer()
        return
    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, lang)
    if callback.message:
        await callback.message.answer(t(lang, "welcome") + "\n\n" + t(lang, "menu"), reply_markup=main_keyboard(lang))
    await callback.answer()


@router.message(F.text)
async def menu_text(message: Message) -> None:
    if not message.from_user or not message.text:
        return
    await db.ensure_user(message.from_user.id)
    lang = await user_language(message.from_user.id)
    text = message.text
    if text in (t(lang, "button_instruction"), "/instruction"):
        await message.answer(t(lang, "instruction"), reply_markup=main_keyboard(lang))
    elif text in (t(lang, "button_language"), "/language"):
        await message.answer(t(lang, "choose_language"), reply_markup=language_keyboard(lang))
    elif text in (t(lang, "button_signal"), "/signal"):
        await show_signal_gate(message, lang)


async def show_signal_gate(message: Message, lang: str) -> None:
    user = await db.get_user(message.from_user.id)
    if user and user["deposited"]:
        await message.answer(t(lang, "send_image"), reply_markup=main_keyboard(lang))
        return
    if user and user["registered"]:
        await message.answer(t(lang, "need_deposit"), reply_markup=main_keyboard(lang))
        return
    markup, _ = await referral_button(message.from_user.id, lang)
    if not markup:
        await message.answer(t(lang, "no_link"), reply_markup=main_keyboard(lang))
        return
    promo = (await db.get_setting("promo")) or ""
    promo_line = f"\n\n{('Промокод: ' if lang == 'ru' else 'Promo code: ')}{promo}" if promo else ""
    await message.answer(t(lang, "need_registration") + promo_line, reply_markup=markup)


@router.message(F.photo)
async def photo_analysis(message: Message, bot: Bot) -> None:
    await process_image(message, bot, message.photo[-1].file_id)


@router.message(F.document)
async def document_analysis(message: Message, bot: Bot) -> None:
    doc = message.document
    if doc and doc.mime_type and doc.mime_type.startswith("image/"):
        await process_image(message, bot, doc.file_id)
    else:
        lang = await user_language(message.from_user.id)
        await message.answer(t(lang, "image_only"))


async def process_image(message: Message, bot: Bot, file_id: str) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    await db.ensure_user(user_id)
    lang = await user_language(user_id)
    allowed, used, analysis_id = await db.reserve_analysis(user_id, settings.daily_analysis_limit)
    if not allowed:
        user = await db.get_user(user_id)
        if user and user["deposited"]:
            await message.answer(t(lang, "limit"))
        elif user and user["registered"]:
            await message.answer(t(lang, "need_deposit"))
        else:
            await show_signal_gate(message, lang)
        return
    status = await message.answer(t(lang, "analyzing"))
    try:
        file_info = await bot.get_file(file_id)
        if not file_info.file_path:
            raise RuntimeError("Telegram returned no file path")
        downloaded = await bot.download_file(file_info.file_path)
        image_data = downloaded.getvalue()
        mime = "image/jpeg"
        if file_info.file_path.lower().endswith(".png"):
            mime = "image/png"
        elif file_info.file_path.lower().endswith(".webp"):
            mime = "image/webp"
        result = await analyze_screenshot(image_data, mime, lang)
        await status.edit_text(result[:4000] + "\n\n" + t(lang, "risk"))
    except Exception:
        log.exception("Screenshot analysis failed for user %s", user_id)
        await db.rollback_analysis(analysis_id)
        await status.edit_text(t(lang, "analysis_error"))


def parse_postback(text: str) -> tuple[str, str] | None:
    fields = [part.strip() for part in text.strip().split("|") if part.strip()]
    if len(fields) < 2:
        return None
    event_index = next((i for i, item in enumerate(fields) if re.search(
        r"first\s*dep|first[_ -]?deposit|deposit|first[_ -]?dep|registration|register|signup|\breg\b",
        item, re.IGNORECASE,
    )), None)
    if event_index is None:
        return None
    click_id = next((item for i, item in enumerate(fields) if i != event_index and item), "")
    return (click_id, fields[event_index]) if click_id else None


@router.channel_post()
async def postback_channel_post(message: Message, bot: Bot) -> None:
    if message.chat.id != settings.postback_channel_id or not message.text:
        return
    parsed = parse_postback(message.text)
    if not parsed:
        log.warning("Ignored unrecognized postback message_id=%s", message.message_id)
        return
    click_id, event = parsed
    activation = await db.activate_event(click_id, event)
    if activation is None:
        log.warning("Postback has unknown click_id; message_id=%s", message.message_id)
        return
    user_id, changed = activation
    if not changed:
        return
    user = await db.get_user(user_id)
    lang = user["language"] if user else "ru"
    is_deposit = any(term in event.lower() for term in ("firstdep", "deposit", "dep"))
    await bot.send_message(user_id, t(lang, "activated" if is_deposit else "registered"))


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp

