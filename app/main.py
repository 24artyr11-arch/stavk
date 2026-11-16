import asyncio
import hmac
import logging
import os
from html import escape
from urllib.parse import parse_qs

import uvicorn
from fastapi import FastAPI
from fastapi import Depends, HTTPException, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from aiogram import Bot

from app.bot import create_dispatcher
from app.config import settings, validate_settings
from app.db import db
from app.texts import TEXTS, t, text_keys

logging.basicConfig(level=logging.INFO)
api = FastAPI(title="Telegram Betting Analysis Bot")
basic_auth = HTTPBasic()


@api.get("/health")
async def health():
    return {"status": "ok"}


async def require_admin(credentials: HTTPBasicCredentials) -> None:
    user_ok = hmac.compare_digest(credentials.username.encode(), settings.admin_username.encode())
    pass_ok = bool(settings.admin_password) and hmac.compare_digest(credentials.password.encode(), settings.admin_password.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Basic"})


@api.get("/admin", response_class=Response)
async def admin_page(credentials: HTTPBasicCredentials = Depends(basic_auth)):
    await require_admin(credentials)
    referral = escape(await db.get_setting("referral_url") or "", quote=True)
    promo = escape(await db.get_setting("promo") or "", quote=True)
    text_fields = []
    for lang, section_name in (("ru", "Русский"), ("en", "English")):
        text_fields.append(f"<h2>{section_name}</h2>")
        for key in text_keys():
            value = escape(t(lang, key))
            label = escape(key)
            text_fields.append(
                f'<label>{label}</label><textarea name="text_{lang}_{key}" rows="3">{value}</textarea>'
            )
    html = f"""<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Настройки бота</title><style>body{{font:16px system-ui;max-width:820px;margin:40px auto;padding:0 16px;background:#10131a;color:#eef}}label{{display:block;margin:20px 0 6px;color:#ccd}}input,textarea{{box-sizing:border-box;width:100%;padding:12px;border-radius:8px;border:1px solid #667;background:#202633;color:#fff;font:inherit}}textarea{{min-height:72px;resize:vertical}}button{{margin-top:20px;padding:12px 22px;border:0;border-radius:8px;background:#3185ff;color:white;font-weight:700;cursor:pointer}}small{{display:block;color:#bbc;margin-top:8px}}h2{{margin-top:36px;border-bottom:1px solid #334;padding-bottom:8px}}</style>
    <h1>Настройки бота</h1><form method="post" action="/admin">
    <h2>Партнёрские настройки</h2><label>Партнёрская ссылка</label><input name="referral_url" value="{referral}" required><small>Используйте параметр sub1 со значением {{click_id}}, например sub1={{click_id}}.</small>
    <label>Промокод</label><input name="promo" value="{promo}" placeholder="Оставьте пустым, чтобы убрать">
    {''.join(text_fields)}
    <button type="submit">Сохранить всё</button></form></html>"""
    return Response(content=html, media_type="text/html; charset=utf-8")


@api.post("/admin", response_class=Response)
async def save_admin_page(request: Request, credentials: HTTPBasicCredentials = Depends(basic_auth)):
    await require_admin(credentials)
    form = parse_qs((await request.body()).decode("utf-8", errors="replace"), keep_blank_values=True)
    referral = form.get("referral_url", [""])[0].strip()
    promo = form.get("promo", [""])[0].strip()
    if not referral.startswith(("https://", "http://")):
        raise HTTPException(status_code=400, detail="Введите корректную ссылку, начинающуюся с http:// или https://")
    await db.set_setting("referral_url", referral)
    await db.set_setting("promo", promo)
    for language in TEXTS:
        for key in text_keys():
            field = f"text_{language}_{key}"
            if field in form:
                await db.set_text(language, key, form[field][0])
    return Response(status_code=303, headers={"Location": "/admin"})


async def serve_http() -> None:
    config = uvicorn.Config(api, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), log_level="info")
    await uvicorn.Server(config).serve()


async def main() -> None:
    validate_settings()
    await db.connect()
    bot = Bot(token=settings.bot_token)
    dp = create_dispatcher()
    try:
        await asyncio.gather(
            dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types() + ["channel_post"]),
            serve_http(),
        )
    finally:
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

