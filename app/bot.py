import logging
import re
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.ai_analysis import analyze_screenshot
from app.config import settings
from app.db import db
from app.texts import category_text_keys, t, text_categories, text_keys, text_label

log = logging.getLogger(__name__)
router = Router()

# Pending admin input is intentionally in memory; a restart cancels unfinished edits.
pending_admin_inputs: dict[int, tuple[str, int, str, str | None, str | None]] = {}


def main_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_instruction"), callback_data="menu:instruction"),
         InlineKeyboardButton(text=t(lang, "button_language"), callback_data="menu:language")],
        [InlineKeyboardButton(text=t(lang, "button_signal"), callback_data="menu:signal")],
    ])


def language_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "language_russian"), callback_data="lang:ru"),
         InlineKeyboardButton(text=t(lang, "language_english"), callback_data="lang:en")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="menu:home")],
    ])


def admin_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_admin_settings"), callback_data="admin:settings")],
        [InlineKeyboardButton(text=t(lang, "button_edit_ru"), callback_data="admin:texts:ru"),
         InlineKeyboardButton(text=t(lang, "button_edit_en"), callback_data="admin:texts:en")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="menu:home")],
    ])


def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_set_link"), callback_data="admin:input:link")],
        [InlineKeyboardButton(text=t(lang, "button_set_promo"), callback_data="admin:input:promo")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="admin:home")],
    ])


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_cancel"), callback_data="admin:cancel")]
    ])


def text_category_keyboard(lang: str, text_lang: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=title, callback_data=f"admin:category:{text_lang}:{category}")]
            for category, title in text_categories(lang)]
    rows.append([InlineKeyboardButton(text=t(lang, "button_back"), callback_data="admin:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def text_picker_keyboard(lang: str, text_lang: str, category: str) -> InlineKeyboardMarkup:
    keys = category_text_keys(category)
    rows = []
    for i in range(0, len(keys), 2):
        row = []
        for key in keys[i:i + 2]:
            label = text_label(lang, key)
            row.append(InlineKeyboardButton(text=label[:60], callback_data=f"admin:view:{text_lang}:{key}:{category}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t(lang, "button_back"), callback_data=f"admin:texts:{text_lang}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def text_view_keyboard(lang: str, text_lang: str, key: str, category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_text_edit"), callback_data=f"admin:edit:{text_lang}:{key}:{category}")],
        [InlineKeyboardButton(text=t(lang, "button_text_reset"), callback_data=f"admin:resetconfirm:{text_lang}:{key}:{category}")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data=f"admin:category:{text_lang}:{category}")],
    ])


def reset_confirm_keyboard(lang: str, text_lang: str, key: str, category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_text_reset_yes"), callback_data=f"admin:reset:{text_lang}:{key}:{category}")],
        [InlineKeyboardButton(text=t(lang, "button_text_reset_no"), callback_data=f"admin:view:{text_lang}:{key}:{category}")],
    ])


def text_view_message(lang: str, text_lang: str, key: str) -> str:
    label = text_label(lang, key)
    current = t(text_lang, key)
    return t(lang, "admin_text_preview").format(label=label, current=current[:3500])


async def user_language(user_id: int) -> str:
    row = await db.get_user(user_id)
    return row["language"] if row else "ru"


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


async def safe_delete(message: Message | None) -> None:
    if not message:
        return
    try:
        await message.delete()
    except Exception:
        log.debug("Could not delete previous bot message", exc_info=True)


async def send_home(bot: Bot, user_id: int, lang: str) -> None:
    await bot.send_message(user_id, t(lang, "welcome") + "\n\n" + t(lang, "menu"), reply_markup=main_keyboard(lang))


async def referral_button(user_id: int, lang: str):
    base = await db.get_setting("referral_url")
    if not base:
        return None
    click_id = await db.create_referral(user_id)
    encoded = quote(click_id, safe="")
    if "{click_id}" in base:
        url = base.replace("{click_id}", encoded)
    elif "{sub1}" in base:
        url = base.replace("{sub1}", encoded)
    else:
        separator = "&" if "?" in base else "?"
        url = f"{base}{separator}sub1={encoded}"
    label = t(lang, "button_register")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, url=url)],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="menu:home")],
    ])


async def show_signal_gate(bot: Bot, user_id: int, lang: str) -> None:
    user = await db.get_user(user_id)
    if user and user["deposited"]:
        await bot.send_message(user_id, t(lang, "send_image"), reply_markup=main_keyboard(lang))
        return
    if user and user["registered"]:
        await bot.send_message(user_id, t(lang, "need_deposit"), reply_markup=main_keyboard(lang))
        return
    markup = await referral_button(user_id, lang)
    if not markup:
        await bot.send_message(user_id, t(lang, "no_link"), reply_markup=main_keyboard(lang))
        return
    promo = (await db.get_setting("promo")) or ""
    promo_line = f"\n\n{t(lang, 'promo_prefix')}{promo}" if promo else ""
    await bot.send_message(user_id, t(lang, "need_registration") + promo_line, reply_markup=markup)


@router.message(CommandStart())
async def start(message: Message) -> None:
    if not message.from_user:
        return
    await db.ensure_user(message.from_user.id)
    lang = await user_language(message.from_user.id)
    await message.answer(t(lang, "welcome") + "\n\n" + t(lang, "menu"), reply_markup=main_keyboard(lang))


@router.message(Command("myid"))
async def my_id(message: Message) -> None:
    if not message.from_user:
        return
    lang = await user_language(message.from_user.id)
    await message.answer(t(lang, "admin_id_reply").format(user_id=message.from_user.id))


@router.message(Command("admin"))
async def open_admin(message: Message) -> None:
    if not message.from_user:
        return
    if not is_admin(message.from_user.id):
        await message.answer(t(await user_language(message.from_user.id), "admin_forbidden"))
        return
    lang = await user_language(message.from_user.id)
    await message.answer(t(lang, "admin_panel"), reply_markup=admin_keyboard(lang))


@router.callback_query(F.data.startswith("menu:"))
async def menu_callback(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.data:
        await callback.answer()
        return
    user_id = callback.from_user.id
    await db.ensure_user(user_id)
    lang = await user_language(user_id)
    action = callback.data.split(":", 1)[1]
    await safe_delete(callback.message)
    if action == "home":
        await send_home(bot, user_id, lang)
    elif action == "instruction":
        await bot.send_message(user_id, t(lang, "instruction"), reply_markup=main_keyboard(lang))
    elif action == "language":
        await bot.send_message(user_id, t(lang, "choose_language"), reply_markup=language_keyboard(lang))
    elif action == "signal":
        await show_signal_gate(bot, user_id, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.data:
        await callback.answer()
        return
    lang = callback.data.partition(":")[2]
    if lang not in ("ru", "en"):
        await callback.answer()
        return
    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, lang)
    await safe_delete(callback.message)
    await send_home(bot, callback.from_user.id, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:"))
async def admin_callback(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.data:
        await callback.answer()
        return
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer(t(await user_language(user_id), "admin_forbidden"), show_alert=True)
        return
    lang = await user_language(user_id)
    parts = callback.data.split(":")
    action = parts[1]
    await safe_delete(callback.message)

    if action == "home":
        await bot.send_message(user_id, t(lang, "admin_panel"), reply_markup=admin_keyboard(lang))
    elif action == "settings":
        await bot.send_message(user_id, t(lang, "admin_choose_setting"), reply_markup=settings_keyboard(lang))
    elif action == "texts" and len(parts) == 3 and parts[2] in ("ru", "en"):
        await bot.send_message(user_id, t(lang, "admin_choose_category"), reply_markup=text_category_keyboard(lang, parts[2]))
    elif action == "category" and len(parts) == 4 and parts[2] in ("ru", "en"):
        valid_categories = {category for category, _ in text_categories(lang)}
        if parts[3] in valid_categories:
            await bot.send_message(
                user_id,
                t(lang, "admin_choose_text"),
                reply_markup=text_picker_keyboard(lang, parts[2], parts[3]),
            )
    elif action == "view" and len(parts) == 5 and parts[2] in ("ru", "en") and parts[3] in text_keys():
        await bot.send_message(
            user_id,
            text_view_message(lang, parts[2], parts[3]),
            reply_markup=text_view_keyboard(lang, parts[2], parts[3], parts[4]),
        )
    elif action == "input" and len(parts) == 3 and parts[2] in ("link", "promo"):
        input_kind = parts[2]
        key = "admin_edit_link_prompt" if input_kind == "link" else "admin_edit_promo_prompt"
        prompt = await bot.send_message(user_id, t(lang, key), reply_markup=cancel_keyboard(lang))
        pending_admin_inputs[user_id] = (input_kind, prompt.message_id, lang, None, None)
    elif action == "edit" and len(parts) == 5 and parts[2] in ("ru", "en") and parts[3] in text_keys():
        text_lang, key, category = parts[2], parts[3], parts[4]
        prompt = await bot.send_message(user_id, t(lang, "admin_text_edit_prompt"), reply_markup=cancel_keyboard(lang))
        pending_admin_inputs[user_id] = ("text", prompt.message_id, text_lang, key, category)
    elif action == "resetconfirm" and len(parts) == 5 and parts[2] in ("ru", "en") and parts[3] in text_keys():
        await bot.send_message(
            user_id,
            t(lang, "admin_text_reset_confirm"),
            reply_markup=reset_confirm_keyboard(lang, parts[2], parts[3], parts[4]),
        )
    elif action == "reset" and len(parts) == 5 and parts[2] in ("ru", "en") and parts[3] in text_keys():
        text_lang, key, category = parts[2], parts[3], parts[4]
        await db.clear_text(text_lang, key)
        await bot.send_message(
            user_id,
            t(lang, "admin_text_reset_done") + "\n\n" + text_view_message(lang, text_lang, key),
            reply_markup=text_view_keyboard(lang, text_lang, key, category),
        )
    elif action == "cancel":
        pending_admin_inputs.pop(user_id, None)
        await bot.send_message(user_id, t(lang, "admin_cancelled"), reply_markup=admin_keyboard(lang))
    await callback.answer()


@router.message(F.photo)
async def photo_analysis(message: Message, bot: Bot) -> None:
    if message.photo:
        await process_image(message, bot, message.photo[-1].file_id)


@router.message(F.document)
async def document_analysis(message: Message, bot: Bot) -> None:
    if not message.from_user:
        return
    doc = message.document
    if doc and doc.mime_type and doc.mime_type.startswith("image/"):
        await process_image(message, bot, doc.file_id)
    else:
        await message.answer(t(await user_language(message.from_user.id), "image_only"))


async def process_image(message: Message, bot: Bot, file_id: str) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    await db.ensure_user(user_id)
    lang = await user_language(user_id)
    allowed, _, analysis_id = await db.reserve_analysis(user_id, settings.daily_analysis_limit)
    if not allowed:
        user = await db.get_user(user_id)
        if user and user["deposited"]:
            await message.answer(t(lang, "limit"), reply_markup=main_keyboard(lang))
        elif user and user["registered"]:
            await message.answer(t(lang, "need_deposit"), reply_markup=main_keyboard(lang))
        else:
            await show_signal_gate(bot, user_id, lang)
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
        await status.edit_text(result[:4000] + "\n\n" + t(lang, "risk"), reply_markup=main_keyboard(lang))
    except Exception:
        log.exception("Screenshot analysis failed for user %s", user_id)
        if analysis_id is not None:
            await db.rollback_analysis(analysis_id)
        await status.edit_text(t(lang, "analysis_error"), reply_markup=main_keyboard(lang))


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
    await bot.send_message(user_id, t(lang, "activated" if is_deposit else "registered"), reply_markup=main_keyboard(lang))


@router.message(F.text)
async def text_input_and_commands(message: Message, bot: Bot) -> None:
    if not message.from_user or not message.text:
        return
    user_id = message.from_user.id
    await db.ensure_user(user_id)
    lang = await user_language(user_id)

    pending = pending_admin_inputs.get(user_id)
    if pending:
        if not is_admin(user_id):
            pending_admin_inputs.pop(user_id, None)
            return
        kind, prompt_id, target_lang, key, category = pending
        value = message.text.strip()
        if kind == "link":
            if not value.startswith(("https://", "http://")):
                await message.answer(t(lang, "admin_invalid_link"), reply_markup=cancel_keyboard(lang))
                return
            await db.set_setting("referral_url", value)
        elif kind == "promo":
            await db.set_setting("promo", "" if value == "-" else value)
        elif kind == "text" and target_lang in ("ru", "en") and key in text_keys():
            await db.set_text(target_lang, key, message.text)
        pending_admin_inputs.pop(user_id, None)
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await bot.delete_message(user_id, prompt_id)
        except Exception:
            pass
        if kind == "text" and key and category:
            await bot.send_message(
                user_id,
                t(lang, "admin_saved") + "\n\n" + text_view_message(lang, target_lang, key),
                reply_markup=text_view_keyboard(lang, target_lang, key, category),
            )
        else:
            await bot.send_message(user_id, t(lang, "admin_saved"), reply_markup=settings_keyboard(lang))
        return

    text = message.text
    if text in ("/instruction", "Инструкция", "Instructions"):
        await message.answer(t(lang, "instruction"), reply_markup=main_keyboard(lang))
    elif text in ("/language", "Язык", "Language"):
        await message.answer(t(lang, "choose_language"), reply_markup=language_keyboard(lang))
    elif text in ("/signal", "Получить сигнал", "Get analysis"):
        await show_signal_gate(bot, user_id, lang)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp

