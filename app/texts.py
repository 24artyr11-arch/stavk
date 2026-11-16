TEXTS = {
    "ru": {
        "button_instruction": "📚 Инструкция",
        "button_language": "🌐 Выбрать язык",
        "button_signal": "🎯 Получить сигнал",
        "language_russian": "🇷🇺 Русский",
        "language_english": "🇬🇧 Английский",
        "welcome": "Привет! Здесь можно отправить скриншот купона для осторожного ИИ-анализа. Анализ не гарантирует выигрыш.",
        "menu": "Главное меню:",
        "instruction": "Как пользоваться:\n1. Нажмите «Получить сигнал».\n2. Создайте новый аккаунт 1win по вашей персональной ссылке.\n3. После подтверждения регистрации внесите депозит любого размера.\n4. Когда postback подтвердит депозит, отправьте сюда скриншот купона.\n5. В примере стратегии предлагается после неудачной ставки удвоить следующую, чтобы попытаться покрыть убыток. Это не гарантирует возврат денег и может быстро увеличить потери; заранее установите лимит и не отыгрывайтесь.\n\nДоступно до 3 анализов за сутки (UTC). Анализ вероятностный и не гарантирует выигрыш.",
        "choose_language": "Выберите язык / Choose language:",
        "need_registration": "Чтобы открыть анализ, сначала зарегистрируйтесь в 1win по персональной ссылке. Используйте промокод, если он указан ниже. Доступ активируется после подтверждения регистрации и первого депозита любого размера.",
        "need_deposit": "Регистрация подтверждена. Внесите первый депозит любого размера по той же партнёрской ссылке. После подтверждения postback доступ откроется автоматически.",
        "send_image": "Доступ открыт. Отправьте скриншот купона одним изображением. Лимит — 3 анализа за сутки по UTC.",
        "no_link": "Ссылка ещё не настроена. Попробуйте позже или обратитесь в поддержку.",
        "no_promo": "Промокод: не задан",
        "limit": "Лимит на сегодня исчерпан: 3 анализа в сутки по UTC. Попробуйте после 00:00 UTC.",
        "analyzing": "Скриншот получен, анализирую…",
        "analysis_error": "Не удалось выполнить анализ. Попробуйте позже; неудачный запрос не списан из лимита.",
        "image_only": "Пожалуйста, отправьте скриншот купона как фото или изображение.",
        "risk": "Ставки связаны с риском потери денег. Не используйте деньги, которые не можете позволить себе потерять.",
        "registered": "Регистрация подтверждена. Теперь дождитесь подтверждения первого депозита.",
        "activated": "Первый депозит подтверждён — доступ к анализу открыт. Отправьте скриншот купона.",
        "admin_help": "Команды администратора:\n/set_referral <URL с {click_id} или {sub1}>\n/set_promo <промокод или ->\n/get_referral\n/get_promo",
        "saved": "Сохранено.",
        "set_referral_usage": "Использование: /set_referral https://...sub1={click_id}",
        "set_promo_usage": "Использование: /set_promo <промокод или ->",
        "referral_unset": "Ссылка не настроена.",
        "promo_unset": "Промокод не задан.",
    },
    "en": {
        "button_instruction": "📚 Instructions",
        "button_language": "🌐 Language",
        "button_signal": "🎯 Get analysis",
        "language_russian": "🇷🇺 Russian",
        "language_english": "🇬🇧 English",
        "welcome": "Hello! Send a betting slip screenshot for a cautious AI analysis. Analysis does not guarantee a win.",
        "menu": "Main menu:",
        "instruction": "How it works:\n1. Tap “Get analysis”.\n2. Create a new 1win account using your personal link.\n3. After registration is confirmed, make a first deposit of any amount.\n4. Once the postback confirms the deposit, send a betting slip screenshot here.\n5. The example strategy suggests doubling the next stake after a loss to try to recover it. This does not guarantee recovery and can increase losses quickly; set a limit in advance and do not chase losses.\n\nUp to 3 analyses per day (UTC). Analysis is probabilistic and does not guarantee a win.",
        "choose_language": "Выберите язык / Choose language:",
        "need_registration": "To unlock analysis, first register at 1win using your personal link. Enter the promo code shown below if provided. Access is enabled after registration and the first deposit of any amount are confirmed.",
        "need_deposit": "Registration confirmed. Make your first deposit of any amount using the same affiliate link. Access will be enabled automatically after the postback is confirmed.",
        "send_image": "Access is enabled. Send one betting slip screenshot as an image. Limit: 3 analyses per day (UTC).",
        "no_link": "The link has not been configured yet. Please try later or contact support.",
        "no_promo": "Promo code: not set",
        "limit": "Today's limit is reached: 3 analyses per day (UTC). Try again after 00:00 UTC.",
        "analyzing": "Screenshot received. Analyzing…",
        "analysis_error": "Analysis failed. Please try again later; this failed request was not counted.",
        "image_only": "Please send the betting slip screenshot as a photo or image.",
        "risk": "Betting carries a risk of losing money. Never stake money you cannot afford to lose.",
        "registered": "Registration confirmed. Please wait for the first deposit confirmation.",
        "activated": "First deposit confirmed — analysis access is enabled. Send a betting slip screenshot.",
        "admin_help": "Admin commands:\n/set_referral <URL containing {click_id} or {sub1}>\n/set_promo <promo code or ->\n/get_referral\n/get_promo",
        "saved": "Saved.",
        "set_referral_usage": "Usage: /set_referral https://...sub1={click_id}",
        "set_promo_usage": "Usage: /set_promo <promo code or ->",
        "referral_unset": "Affiliate link is not set.",
        "promo_unset": "Promo code is not set.",
    },
}

CUSTOM_TEXTS: dict[str, dict[str, str]] = {"ru": {}, "en": {}}


def load_custom_texts(rows: list[dict[str, str]]) -> None:
    for language in CUSTOM_TEXTS:
        CUSTOM_TEXTS[language].clear()
    for row in rows:
        if row.get("language") in CUSTOM_TEXTS:
            CUSTOM_TEXTS[row["language"]][row["key"]] = row["value"]


def set_custom_text(language: str, key: str, value: str) -> None:
    if language in CUSTOM_TEXTS:
        CUSTOM_TEXTS[language][key] = value


def text_keys() -> list[str]:
    return list(TEXTS["ru"].keys())


def t(lang: str, key: str) -> str:
    language = lang if lang in TEXTS else "ru"
    return CUSTOM_TEXTS.get(language, {}).get(key, TEXTS[language].get(key, TEXTS["ru"].get(key, key)))

