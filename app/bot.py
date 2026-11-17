import logging
import re
from typing import Any
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.ai_analysis import analyze_screenshot
from app.config import settings
from app.db import db
from app.texts import category_text_keys, t, text_categories, text_keys, text_label

log = logging.getLogger(__name__)
router = Router()

# Drafts are temporary; only confirmed changes are written to SQLite.
pending_admin_inputs: dict[int, dict[str, Any]] = {}

BUTTON_KEYS = {
    "button_instruction", "button_language", "button_signal", "button_open_app",
    "button_register", "language_russian", "language_english", "button_back",
    "button_cancel", "button_admin", "button_admin_content", "button_admin_analytics",
    "button_admin_grant_access",
    "button_admin_settings", "button_edit_ru", "button_edit_en", "button_set_link",
    "button_set_promo", "button_text_edit", "button_edit_button_label", "button_edit_image",
    "button_remove_image", "button_edit_buttons", "button_edit_promo", "button_save",
    "button_text_reset", "button_text_reset_yes", "button_text_reset_no",
}

MESSAGE_BUTTONS = {
    "menu": ["button_instruction", "button_language", "button_signal"],
    "instruction": ["button_instruction", "button_language", "button_signal"],
    "need_registration": ["button_register", "button_back"],
    "need_deposit": ["button_instruction", "button_language", "button_signal"],
    "send_image": ["button_open_app", "button_back"],
    "no_link": ["button_instruction", "button_language", "button_signal"],
    "limit": ["button_instruction", "button_language", "button_signal"],
    "analysis_error": ["button_instruction", "button_language", "button_signal"],
    "image_only": ["button_instruction", "button_language", "button_signal"],
    "registered": ["button_instruction", "button_language", "button_signal"],
    "activated": ["button_instruction", "button_language", "button_signal"],
    "choose_language": ["language_russian", "language_english", "button_back"],
}

MEDIA_SUPPORTED_KEYS = {
    "welcome", "menu", "instruction", "choose_language", "need_registration", "need_deposit",
    "send_image", "no_link", "limit", "analyzing", "analysis_error", "image_only",
    "risk", "registered", "activated",
}

EDITABLE_MESSAGE_KEYS = (
    "menu", "instruction", "need_registration", "registration_error", "need_deposit", "deposit_error",
)


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
        [InlineKeyboardButton(text=t(lang, "button_admin_content"), callback_data="admin:content")],
        [InlineKeyboardButton(text=t(lang, "button_admin_analytics"), callback_data="admin:analytics")],
        [InlineKeyboardButton(text=t(lang, "button_admin_grant_access"), callback_data="admin:grantaccess")],
        [InlineKeyboardButton(text=t(lang, "button_admin_settings"), callback_data="admin:settings")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="menu:home")],
    ])


def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_set_link"), callback_data="admin:input:link")],
        [InlineKeyboardButton(text=t(lang, "button_set_promo"), callback_data="admin:input:promo")],
        [InlineKeyboardButton(text=t(lang, "button_set_webapp"), callback_data="admin:input:webapp_url")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="admin:home")],
    ])


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_cancel"), callback_data="admin:cancel")]
    ])


def draft_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_save"), callback_data="admin:save")],
        [InlineKeyboardButton(text=t(lang, "button_cancel"), callback_data="admin:cancel")],
    ])


def text_category_keyboard(lang: str, text_lang: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=title, callback_data=f"admin:category:{text_lang}:{category}")]
            for category, title in text_categories(lang)]
    rows.append([InlineKeyboardButton(text=t(lang, "button_back"), callback_data="admin:content")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def text_picker_keyboard(lang: str, text_lang: str, category: str) -> InlineKeyboardMarkup:
    keys = category_text_keys(category)
    rows = []
    for i in range(0, len(keys), 2):
        rows.append([
            InlineKeyboardButton(
                text=text_label(lang, key)[:60],
                callback_data=f"admin:view:{text_lang}:{key}:{category}",
            )
            for key in keys[i:i + 2]
        ])
    rows.append([InlineKeyboardButton(text=t(lang, "button_back"), callback_data=f"admin:texts:{text_lang}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_message_picker_keyboard(lang: str, text_lang: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(
        text=text_label(lang, key),
        callback_data=f"admin:view:{text_lang}:{key}:messages",
    )] for key in EDITABLE_MESSAGE_KEYS]
    rows.append([InlineKeyboardButton(text=t(lang, "button_back"), callback_data="admin:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def simple_message_editor_keyboard(lang: str, text_lang: str, key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t(lang, "button_text_edit"),
            callback_data=f"admin:edittext:{text_lang}:{key}:messages",
        )],
        [InlineKeyboardButton(
            text=t(lang, "button_back"),
            callback_data=f"admin:texts:{text_lang}",
        )],
    ])


async def send_simple_message_editor(
    bot: Bot,
    user_id: int,
    lang: str,
    text_lang: str,
    key: str,
    notice: str | None = None,
) -> None:
    text = format_text(
        lang,
        "admin_text_preview",
        label=text_label(lang, key),
        current=t(text_lang, key)[:3200],
    )
    if notice:
        text = f"{notice}\n\n{text}"
    await bot.send_message(
        user_id,
        text,
        reply_markup=simple_message_editor_keyboard(lang, text_lang, key),
    )


def button_picker_keyboard(lang: str, text_lang: str, parent_key: str, parent_category: str) -> InlineKeyboardMarkup:
    keys = MESSAGE_BUTTONS.get(parent_key, [])
    rows = [[InlineKeyboardButton(
        text=text_label(lang, key)[:60],
        callback_data=f"admin:button:{text_lang}:{key}:{parent_key}",
    )] for key in keys]
    rows.append([InlineKeyboardButton(
        text=t(lang, "button_back"),
        callback_data=f"admin:view:{text_lang}:{parent_key}:{parent_category}",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def button_preview_keyboard(
    lang: str,
    text_lang: str,
    button_key: str,
    parent_key: str,
    parent_category: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t(lang, "button_edit_button_label"),
            callback_data=(
                f"admin:editbutton:{text_lang}:{button_key}"
                if button_key == parent_key else f"admin:editbutton:{text_lang}:{button_key}:{parent_key}"
            ),
        )],
        [InlineKeyboardButton(
            text=t(lang, "button_text_reset"),
            callback_data=f"admin:resetconfirm:{text_lang}:{button_key}:buttons",
        )],
        [InlineKeyboardButton(
            text=t(lang, "button_back"),
            callback_data=f"admin:view:{text_lang}:{parent_key}:{parent_category}",
        )],
    ])


def text_view_keyboard(
    lang: str,
    text_lang: str,
    key: str,
    category: str,
    has_media: bool,
) -> InlineKeyboardMarkup:
    if key in BUTTON_KEYS:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=t(lang, "button_edit_button_label"),
                callback_data=f"admin:editbutton:{text_lang}:{key}",
            )],
            [InlineKeyboardButton(
                text=t(lang, "button_text_reset"),
                callback_data=f"admin:resetconfirm:{text_lang}:{key}:{category}",
            )],
            [InlineKeyboardButton(text=t(lang, "button_back"), callback_data=f"admin:category:{text_lang}:{category}")],
        ])

    rows = [[InlineKeyboardButton(
        text=t(lang, "button_text_edit"),
        callback_data=f"admin:edittext:{text_lang}:{key}:{category}",
    )]]
    if key in MEDIA_SUPPORTED_KEYS:
        rows.append([InlineKeyboardButton(
            text=t(lang, "button_edit_image"),
            callback_data=f"admin:editimage:{text_lang}:{key}:{category}",
        )])
    if has_media and key in MEDIA_SUPPORTED_KEYS:
        rows.append([InlineKeyboardButton(
            text=t(lang, "button_remove_image"),
            callback_data=f"admin:removeimage:{text_lang}:{key}:{category}",
        )])
    if key == "need_registration":
        rows.append([InlineKeyboardButton(
            text=t(lang, "button_edit_promo"),
            callback_data=f"admin:messagepromo:{text_lang}:{key}:{category}",
        )])
    if key in MESSAGE_BUTTONS:
        rows.append([InlineKeyboardButton(
            text=t(lang, "button_edit_buttons"),
            callback_data=f"admin:buttons:{text_lang}:{key}:{category}",
        )])
    rows.append([InlineKeyboardButton(
        text=t(lang, "button_text_reset"),
        callback_data=f"admin:resetconfirm:{text_lang}:{key}:{category}",
    )])
    rows.append([InlineKeyboardButton(text=t(lang, "button_back"), callback_data=f"admin:category:{text_lang}:{category}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reset_confirm_keyboard(lang: str, text_lang: str, key: str, category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_text_reset_yes"), callback_data=f"admin:reset:{text_lang}:{key}:{category}")],
        [InlineKeyboardButton(text=t(lang, "button_text_reset_no"), callback_data=f"admin:view:{text_lang}:{key}:{category}")],
    ])


def text_view_message(lang: str, text_lang: str, key: str) -> str:
    label = text_label(lang, key)
    current = t(text_lang, key)
    return format_text(lang, "admin_text_preview", label=label, current=current[:3200])


def category_for_key(key: str) -> str:
    for category, keys in (("user_messages", category_text_keys("user_messages")),
                           ("buttons", category_text_keys("buttons")),
                           ("affiliate", category_text_keys("affiliate"))):
        if key in keys:
            return category
    return "admin"


async def send_text_editor_view(
    bot: Bot,
    user_id: int,
    lang: str,
    text_lang: str,
    key: str,
    category: str,
    notice: str | None = None,
) -> None:
    has_media = bool(await db.get_text_media(text_lang, key))
    if key in BUTTON_KEYS:
        text = format_text(lang, "admin_button_preview",
            label=text_label(lang, key), current=t(text_lang, key)[:3200]
        )
    else:
        if key in MEDIA_SUPPORTED_KEYS:
            media_status = t(lang, "admin_image_attached" if has_media else "admin_image_missing")
            text = format_text(lang, "admin_component_prompt",
                label=text_label(lang, key), current=t(text_lang, key)[:3100], media_status=media_status
            )
        else:
            text = format_text(lang, "admin_text_preview",
                label=text_label(lang, key), current=t(text_lang, key)[:3200]
            )
    if notice:
        text = f"{notice}\n\n{text}"
    await bot.send_message(
        user_id,
        text,
        reply_markup=text_view_keyboard(lang, text_lang, key, category, has_media),
    )


async def user_language(user_id: int) -> str:
    row = await db.get_user(user_id)
    return row["language"] if row else "ru"


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def format_text(lang: str, key: str, **values: Any) -> str:
    template = t(lang, key)
    try:
        return template.format(**values)
    except (KeyError, IndexError, ValueError):
        return template


async def safe_delete(message: Message | None) -> None:
    if not message:
        return
    try:
        await message.delete()
    except Exception:
        log.debug("Could not delete previous bot message", exc_info=True)


async def send_user_content(
    bot: Bot,
    user_id: int,
    lang: str,
    key: str,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> list[Message]:
    file_id = await db.get_text_media(lang, key)
    if not file_id:
        return [await bot.send_message(user_id, text, reply_markup=reply_markup)]
    if len(text) <= 1024:
        return [await bot.send_photo(user_id, file_id, caption=text, reply_markup=reply_markup)]
    photo = await bot.send_photo(user_id, file_id)
    message = await bot.send_message(user_id, text, reply_markup=reply_markup)
    return [photo, message]


async def send_home(bot: Bot, user_id: int, lang: str) -> None:
    await send_user_content(bot, user_id, lang, "menu", t(lang, "menu"), reply_markup=main_keyboard(lang))


async def miniapp_url() -> str:
    return (await db.get_setting("webapp_url")) or settings.webapp_url


async def referral_url(user_id: int) -> str | None:
    base = await db.get_setting("referral_url")
    if not base:
        return None
    click_id = await db.get_latest_referral_click_id(user_id)
    if not click_id:
        click_id = await db.create_referral(user_id)
    encoded = quote(click_id, safe="")
    if "{click_id}" in base:
        url = base.replace("{click_id}", encoded)
    elif "{sub1}" in base:
        url = base.replace("{sub1}", encoded)
    else:
        separator = "&" if "?" in base else "?"
        url = f"{base}{separator}sub1={encoded}"
    return url


async def referral_button(user_id: int, lang: str):
    url = await referral_url(user_id)
    if not url:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_register"), url=url)],
        [InlineKeyboardButton(text=t(lang, "button_check_registration"), callback_data="gate:registration")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="menu:home")],
    ])


async def deposit_button(user_id: int, lang: str):
    url = await referral_url(user_id)
    if not url:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "button_make_deposit"), url=url)],
        [InlineKeyboardButton(text=t(lang, "button_check_deposit"), callback_data="gate:deposit")],
        [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="menu:home")],
    ])


async def show_signal_gate(bot: Bot, user_id: int, lang: str) -> None:
    user = await db.get_user(user_id)
    if user and (user["deposited"] or user["access_granted"]):
        markup = main_keyboard(lang)
        url = await miniapp_url()
        if url:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t(lang, "button_open_app"), web_app=WebAppInfo(url=url))],
                [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="menu:home")],
            ])
        await send_user_content(bot, user_id, lang, "send_image", t(lang, "send_image"), reply_markup=markup)
        return
    if user and user["registered"]:
        markup = await deposit_button(user_id, lang)
        if not markup:
            await send_user_content(bot, user_id, lang, "no_link", t(lang, "no_link"), reply_markup=main_keyboard(lang))
            return
        await send_user_content(bot, user_id, lang, "need_deposit", t(lang, "need_deposit"), reply_markup=markup)
        return
    markup = await referral_button(user_id, lang)
    if not markup:
        await send_user_content(bot, user_id, lang, "no_link", t(lang, "no_link"), reply_markup=main_keyboard(lang))
        return
    promo = (await db.get_setting("promo")) or ""
    registration_text = t(lang, "need_registration")
    if promo:
        registration_text += f"\n\n{t(lang, 'promo_prefix')}{promo}"
    await send_user_content(
        bot, user_id, lang, "need_registration", registration_text, reply_markup=markup
    )


async def begin_admin_input(
    bot: Bot,
    user_id: int,
    lang: str,
    kind: str,
    target_lang: str | None = None,
    key: str | None = None,
    category: str | None = None,
    return_key: str | None = None,
    return_category: str | None = None,
) -> None:
    prompt_key = {
        "link": "admin_edit_link_prompt",
        "promo": "admin_edit_promo_prompt",
        "webapp_url": "admin_edit_webapp_prompt",
        "media": "admin_photo_prompt",
        "grant_access": "admin_grant_access_prompt",
    }.get(kind, "admin_text_edit_prompt")
    prompt = await bot.send_message(user_id, t(lang, prompt_key), reply_markup=cancel_keyboard(lang))
    pending_admin_inputs[user_id] = {
        "kind": kind,
        "mode": "waiting",
        "prompt_id": prompt.message_id,
        "target_lang": target_lang,
        "key": key,
        "category": category,
        "return_key": return_key or key,
        "return_category": return_category or category,
        "language": lang,
    }


async def send_admin_return(
    bot: Bot,
    user_id: int,
    lang: str,
    pending: dict[str, Any],
    notice: str,
) -> None:
    target_lang = pending.get("target_lang")
    key = pending.get("return_key") or pending.get("key")
    category = pending.get("return_category") or pending.get("category")
    if pending.get("kind") == "promo":
        promo = (await db.get_setting("promo")) or "—"
        notice += "\n" + format_text(lang, "admin_current_promo", value=promo)
    if pending.get("kind") == "webapp_url":
        current_url = await miniapp_url() or "—"
        notice += "\n" + format_text(lang, "admin_current_webapp", value=current_url)
    if pending.get("kind") == "text" and pending.get("key") in BUTTON_KEYS:
        label = t(pending.get("target_lang", lang), pending["key"])
        notice += "\n" + format_text(lang, "admin_button_saved", value=label)
    if pending.get("kind") == "grant_access":
        await bot.send_message(user_id, notice, reply_markup=admin_keyboard(lang))
        return
    if pending.get("kind") == "text" and category == "messages" and target_lang in ("ru", "en") and key in EDITABLE_MESSAGE_KEYS:
        await send_simple_message_editor(bot, user_id, lang, target_lang, key, notice=notice)
        return
    if target_lang in ("ru", "en") and key in text_keys() and category:
        await send_text_editor_view(bot, user_id, lang, target_lang, key, category, notice=notice)
    else:
        await bot.send_message(user_id, notice, reply_markup=settings_keyboard(lang))


async def handle_admin_text_input(message: Message, bot: Bot, pending: dict[str, Any]) -> None:
    user_id = message.from_user.id
    lang = pending.get("language") or await user_language(user_id)
    kind = pending["kind"]
    if pending.get("mode") != "waiting":
        await message.answer(t(lang, "admin_use_save_cancel"))
        return
    if kind == "media":
        await message.answer(t(lang, "admin_expected_photo"), reply_markup=cancel_keyboard(lang))
        return

    value = message.text.strip()
    if kind == "link" and not value.startswith(("https://", "http://")):
        await message.answer(t(lang, "admin_invalid_link"), reply_markup=cancel_keyboard(lang))
        return
    if kind == "webapp_url" and value != "-" and (not value.startswith("https://") or any(ch.isspace() for ch in value)):
        await message.answer(t(lang, "admin_invalid_webapp"), reply_markup=cancel_keyboard(lang))
        return
    target_id = None
    if kind == "grant_access":
        if not value.isdecimal() or int(value) <= 0 or int(value) > (1 << 52) - 1:
            await message.answer(t(lang, "admin_invalid_telegram_id"), reply_markup=cancel_keyboard(lang))
            return
        target_id = int(value)
    if kind == "text" and not value:
        await message.answer(t(lang, "admin_expected_text"), reply_markup=cancel_keyboard(lang))
        return
    max_length = 2048 if kind in ("link", "webapp_url") else (3500 if kind == "text" else 100)
    if len(value) > max_length:
        await message.answer(t(lang, "admin_expected_text"), reply_markup=cancel_keyboard(lang))
        return

    await safe_delete(message)
    try:
        await bot.delete_message(user_id, pending["prompt_id"])
    except Exception:
        pass
    pending["mode"] = "confirm"
    pending["draft"] = "" if kind in ("promo", "webapp_url") and value == "-" else value
    if kind == "text":
        target_lang = pending["target_lang"]
        key = pending["key"]
        preview = format_text(lang, "admin_draft_text", label=text_label(lang, key), draft=value[:3300])
    elif kind == "grant_access":
        pending["draft"] = str(target_id)
        preview = format_text(lang, "admin_draft_grant_access", user_id=target_id)
    elif kind == "promo":
        preview = format_text(lang, "admin_draft_promo", draft=pending["draft"] or "—")
    elif kind == "webapp_url":
        preview = format_text(
            lang,
            "admin_draft_webapp",
            draft=pending["draft"] or t(lang, "admin_webapp_env_fallback"),
        )
    else:
        preview = format_text(lang, "admin_draft_link", draft=value[:2000])
    await bot.send_message(user_id, preview, reply_markup=draft_keyboard(lang))


async def handle_admin_photo(message: Message, bot: Bot, file_id: str) -> bool:
    if not message.from_user or not is_admin(message.from_user.id):
        return False
    user_id = message.from_user.id
    pending = pending_admin_inputs.get(user_id)
    if not pending:
        return False
    lang = pending.get("language") or await user_language(user_id)
    if pending.get("mode") != "waiting" or pending.get("kind") != "media":
        hint = t(lang, "admin_expected_text") if pending.get("mode") == "waiting" else t(lang, "admin_use_save_cancel")
        await message.answer(hint)
        return True
    await safe_delete(message)
    try:
        await bot.delete_message(user_id, pending["prompt_id"])
    except Exception:
        pass
    pending["mode"] = "confirm"
    pending["draft"] = file_id
    caption = text_label(lang, pending["key"]) + "\n\n" + t(lang, "admin_use_save_cancel")
    await bot.send_photo(user_id, file_id, caption=caption, reply_markup=draft_keyboard(lang))
    return True


async def commit_admin_draft(bot: Bot, user_id: int, lang: str) -> bool:
    pending = pending_admin_inputs.get(user_id)
    if not pending or pending.get("mode") != "confirm":
        return False
    kind = pending["kind"]
    if kind == "text":
        await db.set_text(pending["target_lang"], pending["key"], pending["draft"])
    elif kind == "media":
        if pending["draft"] is None:
            await db.clear_text_media(pending["target_lang"], pending["key"])
        else:
            await db.set_text_media(pending["target_lang"], pending["key"], pending["draft"])
    elif kind == "promo":
        await db.set_setting("promo", pending["draft"])
    elif kind == "link":
        await db.set_setting("referral_url", pending["draft"])
    elif kind == "webapp_url":
        await db.set_setting("webapp_url", pending["draft"])
    elif kind == "grant_access":
        target_id = int(pending["draft"])
        newly_granted = await db.grant_manual_access(target_id, user_id)
        target = await db.get_user(target_id)
        target_lang = target["language"] if target and target["language"] in ("ru", "en") else "ru"
        try:
            await bot.send_message(target_id, t(target_lang, "manual_access_granted"), reply_markup=main_keyboard(target_lang))
            delivery_status = t(lang, "admin_notification_sent")
        except Exception:
            log.info("Could not notify Telegram user %s about manually granted access", target_id, exc_info=True)
            delivery_status = t(lang, "admin_notification_not_sent")
        access_status = t(lang, "admin_access_new" if newly_granted else "admin_access_existing")
        notice = format_text(
            lang,
            "admin_access_granted_admin",
            user_id=target_id,
            access_status=access_status,
            delivery_status=delivery_status,
        )
        pending_admin_inputs.pop(user_id, None)
        await send_admin_return(bot, user_id, lang, pending, notice)
        return True
    else:
        return False
    pending_admin_inputs.pop(user_id, None)
    await send_admin_return(bot, user_id, lang, pending, t(lang, "admin_saved"))
    return True


async def cancel_admin_draft(bot: Bot, user_id: int, lang: str) -> None:
    pending = pending_admin_inputs.pop(user_id, None)
    if pending:
        if pending.get("mode") == "waiting" and pending.get("prompt_id"):
            try:
                await bot.delete_message(user_id, pending["prompt_id"])
            except Exception:
                pass
        await send_admin_return(bot, user_id, lang, pending, t(lang, "admin_cancelled"))
    else:
        await bot.send_message(user_id, t(lang, "admin_cancelled"), reply_markup=admin_keyboard(lang))


@router.message(CommandStart())
async def start(message: Message, bot: Bot) -> None:
    if not message.from_user:
        return
    await db.ensure_user(message.from_user.id)
    await safe_delete(message)
    await send_home(bot, message.from_user.id, await user_language(message.from_user.id))


@router.message(Command("myid"))
async def my_id(message: Message) -> None:
    if not message.from_user:
        return
    lang = await user_language(message.from_user.id)
    await message.answer(format_text(lang, "admin_id_reply", user_id=message.from_user.id))


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
        await send_user_content(bot, user_id, lang, "instruction", t(lang, "instruction"), main_keyboard(lang))
    elif action == "language":
        await send_user_content(bot, user_id, lang, "choose_language", t(lang, "choose_language"), language_keyboard(lang))
    elif action == "signal":
        await show_signal_gate(bot, user_id, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("gate:"))
async def gate_callback(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.from_user or not callback.data:
        await callback.answer()
        return
    user_id = callback.from_user.id
    await db.ensure_user(user_id)
    lang = await user_language(user_id)
    action = callback.data.partition(":")[2]
    await safe_delete(callback.message)
    user = await db.get_user(user_id)

    if user and (user["deposited"] or user["access_granted"]):
        await show_signal_gate(bot, user_id, lang)
    elif action == "registration" and user and user["registered"]:
        await show_signal_gate(bot, user_id, lang)
    elif action == "deposit" and user and user["registered"]:
        markup = await deposit_button(user_id, lang)
        if markup:
            await send_user_content(bot, user_id, lang, "deposit_error", t(lang, "deposit_error"), reply_markup=markup)
        else:
            await send_user_content(bot, user_id, lang, "no_link", t(lang, "no_link"), reply_markup=main_keyboard(lang))
    else:
        markup = await referral_button(user_id, lang)
        if markup:
            await send_user_content(
                bot, user_id, lang, "registration_error", t(lang, "registration_error"), reply_markup=markup
            )
        else:
            await send_user_content(bot, user_id, lang, "no_link", t(lang, "no_link"), reply_markup=main_keyboard(lang))
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
    elif action == "content":
        await bot.send_message(user_id, t(lang, "admin_choose_language"), reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "button_edit_ru"), callback_data="admin:texts:ru")],
            [InlineKeyboardButton(text=t(lang, "button_edit_en"), callback_data="admin:texts:en")],
            [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="admin:home")],
        ]))
    elif action == "analytics":
        analytics = await db.get_user_analytics()
        await bot.send_message(user_id, format_text(lang, "admin_analytics", **analytics), reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "button_admin_analytics"), callback_data="admin:analytics")],
            [InlineKeyboardButton(text=t(lang, "button_back"), callback_data="admin:home")],
        ]))
    elif action == "grantaccess":
        await begin_admin_input(bot, user_id, lang, "grant_access")
    elif action == "settings":
        await bot.send_message(user_id, t(lang, "admin_choose_setting"), reply_markup=settings_keyboard(lang))
    elif action == "texts" and len(parts) == 3 and parts[2] in ("ru", "en"):
        await bot.send_message(
            user_id,
            t(lang, "admin_choose_text"),
            reply_markup=admin_message_picker_keyboard(lang, parts[2]),
        )
    elif action == "view" and len(parts) == 5 and parts[2] in ("ru", "en") and parts[3] in EDITABLE_MESSAGE_KEYS and parts[4] == "messages":
        await send_simple_message_editor(bot, user_id, lang, parts[2], parts[3])
    elif action == "edittext" and len(parts) == 5 and parts[2] in ("ru", "en") and parts[3] in EDITABLE_MESSAGE_KEYS and parts[4] == "messages":
        await begin_admin_input(bot, user_id, lang, "text", parts[2], parts[3], "messages")
    elif action == "input" and len(parts) == 3 and parts[2] in ("link", "promo", "webapp_url"):
        await begin_admin_input(bot, user_id, lang, parts[2])
    elif action == "save":
        saved = await commit_admin_draft(bot, user_id, lang)
        if not saved:
            await callback.answer(t(lang, "admin_use_save_cancel"), show_alert=True)
            return
    elif action == "cancel":
        await cancel_admin_draft(bot, user_id, lang)
    await callback.answer()


@router.message(F.photo)
async def photo_analysis(message: Message, bot: Bot) -> None:
    if not message.photo:
        return
    if await handle_admin_photo(message, bot, message.photo[-1].file_id):
        return
    await process_image(message, bot, message.photo[-1].file_id)


@router.message(F.document)
async def document_analysis(message: Message, bot: Bot) -> None:
    if not message.from_user:
        return
    doc = message.document
    if doc and doc.mime_type and doc.mime_type.startswith("image/"):
        if await handle_admin_photo(message, bot, doc.file_id):
            return
        await process_image(message, bot, doc.file_id)
    else:
        await send_user_content(
            bot, message.from_user.id, await user_language(message.from_user.id),
            "image_only", t(await user_language(message.from_user.id), "image_only"),
        )


async def process_image(message: Message, bot: Bot, file_id: str) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    await db.ensure_user(user_id)
    lang = await user_language(user_id)
    allowed, _, analysis_id = await db.reserve_analysis(user_id, settings.daily_analysis_limit)
    if not allowed:
        user = await db.get_user(user_id)
        if user and (user["deposited"] or user["access_granted"]):
            await send_user_content(bot, user_id, lang, "limit", t(lang, "limit"), main_keyboard(lang))
        else:
            await show_signal_gate(bot, user_id, lang)
        return
    statuses = await send_user_content(bot, user_id, lang, "analyzing", t(lang, "analyzing"))
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
        for status in statuses:
            await safe_delete(status)
        await bot.send_message(user_id, result[:4000])
        await send_user_content(bot, user_id, lang, "risk", t(lang, "risk"), main_keyboard(lang))
    except Exception:
        log.exception("Screenshot analysis failed for user %s", user_id)
        if analysis_id is not None:
            await db.rollback_analysis(analysis_id)
        for status in statuses:
            await safe_delete(status)
        await send_user_content(bot, user_id, lang, "analysis_error", t(lang, "analysis_error"), main_keyboard(lang))


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
    await show_signal_gate(bot, user_id, lang)


@router.message(F.text)
async def text_input_and_commands(message: Message, bot: Bot) -> None:
    if not message.from_user or not message.text:
        return
    user_id = message.from_user.id
    await db.ensure_user(user_id)
    lang = await user_language(user_id)
    pending = pending_admin_inputs.get(user_id)
    if pending and is_admin(user_id):
        if message.text.strip().lower() == "/cancel":
            await safe_delete(message)
            await cancel_admin_draft(bot, user_id, lang)
        else:
            await handle_admin_text_input(message, bot, pending)
        return

    text = message.text
    if text in ("/instruction", "Инструкция", "Instructions"):
        await send_user_content(bot, user_id, lang, "instruction", t(lang, "instruction"), main_keyboard(lang))
    elif text in ("/language", "Язык", "Language"):
        await send_user_content(bot, user_id, lang, "choose_language", t(lang, "choose_language"), language_keyboard(lang))
    elif text in ("/signal", "Получить сигнал", "Get analysis"):
        await show_signal_gate(bot, user_id, lang)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp

