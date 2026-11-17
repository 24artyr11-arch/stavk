import hashlib
import hmac
import json
import logging
import time
from pathlib import Path
from urllib.parse import parse_qsl

from aiohttp import web

from app.ai_analysis import analyze_screenshot
from app.config import settings
from app.db import db

log = logging.getLogger(__name__)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_INIT_DATA_AGE_SECONDS = 24 * 60 * 60
ALLOWED_SPORTS = {
    "football", "basketball", "hockey", "tennis", "volleyball",
    "table_tennis", "boxing_mma", "esports", "other",
}


def validate_init_data(init_data: str) -> dict | None:
    if not init_data or len(init_data) > 8192:
        return None
    try:
        fields_list = parse_qsl(init_data, keep_blank_values=True, strict_parsing=True)
        fields = dict(fields_list)
        if len(fields) != len(fields_list):
            return None
        received_hash = fields.pop("hash", "")
        auth_date = int(fields.get("auth_date", "0"))
        now = int(time.time())
        if not received_hash or auth_date <= 0 or auth_date > now + 60:
            return None
        if now - auth_date > MAX_INIT_DATA_AGE_SECONDS:
            return None
        check_string = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
        secret_key = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
        expected_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_hash, received_hash):
            return None
        user = json.loads(fields.get("user", "{}"))
        if not isinstance(user, dict) or not isinstance(user.get("id"), int):
            return None
        return user
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def telegram_user(request: web.Request) -> dict | None:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("tma "):
        return None
    return validate_init_data(authorization[4:].strip())


def error_response(message: str, code: str, status: int) -> web.Response:
    return web.json_response({"error": message, "code": code}, status=status)


async def authenticated_user(request: web.Request):
    user_data = telegram_user(request)
    if not user_data:
        return None, error_response("Open this app from the Telegram bot again.", "invalid_telegram_data", 401)
    user_id = user_data["id"]
    await db.ensure_user(user_id)
    user = await db.get_user(user_id)
    return user, None


async def index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB_DIR / "index.html")


async def health(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def api_me(request: web.Request) -> web.Response:
    user, failure = await authenticated_user(request)
    if failure:
        return failure
    user_id = int(user["telegram_id"])
    used = await db.get_analysis_usage(user_id)
    return web.json_response({
        "language": user["language"],
        "authorized": bool(user["deposited"] or user["access_granted"]),
        "remaining": max(0, settings.daily_analysis_limit - used),
        "limit": settings.daily_analysis_limit,
    })


async def api_language(request: web.Request) -> web.Response:
    user, failure = await authenticated_user(request)
    if failure:
        return failure
    try:
        payload = await request.json()
    except (json.JSONDecodeError, ValueError):
        return error_response("Invalid request.", "invalid_request", 400)
    language = payload.get("language") if isinstance(payload, dict) else None
    if language not in ("ru", "en"):
        return error_response("Choose Russian or English.", "invalid_language", 400)
    await db.set_language(int(user["telegram_id"]), language)
    return web.json_response({"language": language})


def image_mime(image: bytes) -> str | None:
    if image.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(image) >= 12 and image[:4] == b"RIFF" and image[8:12] == b"WEBP":
        return "image/webp"
    return None


async def api_analyze(request: web.Request) -> web.Response:
    user, failure = await authenticated_user(request)
    if failure:
        return failure
    user_id = int(user["telegram_id"])
    if not (user["deposited"] or user["access_granted"]):
        return error_response("Analysis access is not active yet.", "deposit_required", 403)

    try:
        form = await request.post()
    except (web.HTTPRequestEntityTooLarge, ValueError):
        return error_response("Image is too large. Maximum size is 10 MB.", "image_too_large", 413)
    upload = form.get("image")
    sport = form.get("sport", "")
    if not hasattr(upload, "file"):
        return error_response("Choose a screenshot first.", "image_required", 400)
    if not isinstance(sport, str) or sport not in ALLOWED_SPORTS:
        return error_response("Choose a sport from the list.", "sport_required", 400)
    image = upload.file.read(MAX_IMAGE_BYTES + 1)
    if len(image) > MAX_IMAGE_BYTES:
        return error_response("Image is too large. Maximum size is 10 MB.", "image_too_large", 413)
    mime_type = image_mime(image)
    if mime_type is None:
        return error_response("Use a JPEG, PNG, or WebP screenshot.", "unsupported_image", 400)

    allowed, used, analysis_id = await db.reserve_analysis(user_id, settings.daily_analysis_limit)
    if not allowed:
        current_user = await db.get_user(user_id)
        if not current_user or not (current_user["deposited"] or current_user["access_granted"]):
            return error_response("Analysis access is not active yet.", "deposit_required", 403)
        return web.json_response({
            "error": "Daily analysis limit reached.",
            "code": "daily_limit",
            "used": used,
            "remaining": 0,
            "limit": settings.daily_analysis_limit,
        }, status=429)

    try:
        result = await analyze_screenshot(image, mime_type, user["language"], sport=sport)
    except Exception:
        log.exception("Mini App image analysis failed for user %s", user_id)
        if analysis_id is not None:
            await db.rollback_analysis(analysis_id)
        return error_response("Analysis failed. Please try again.", "analysis_failed", 502)

    return web.json_response({
        "result": result,
        "used": used,
        "remaining": max(0, settings.daily_analysis_limit - used),
        "limit": settings.daily_analysis_limit,
    })


def create_web_app() -> web.Application:
    app = web.Application(client_max_size=MAX_IMAGE_BYTES + 64 * 1024)
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    app.router.add_get("/api/me", api_me)
    app.router.add_post("/api/language", api_language)
    app.router.add_post("/api/analyze", api_analyze)
    app.router.add_static("/static/", WEB_DIR, show_index=False)
    return app

